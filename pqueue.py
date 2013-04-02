import os, errno, fcntl, struct, shutil, tempfile

class PersistentQueue(object):
    '''A persistent queue class that backs records put onto it into a circular
    disk-backed buffer.
    
    The buffer file is pre-_allocated and has a fixed maximum record size. It can
    be resized dynamically by calling the resize() method.

    Sample usage:

    q = PersistentQueue('/tmp/foo.q', 10, 128)

    q.lock()
    q.put(b'a')
    q.put(b'b')
    q.put(b'c')
    q.unlock()

    # other processing

    while True:
        q.lock()
        rec_id, record = q.get()
        if rec_id is None:
            q.unlock()
            break

        # process record

        q.task_complete(rec_id)
        q.unlock()
    '''


    FILE_HEADER = struct.Struct('!L Q Q Q Q') # version, record_count, record_size, first, last
    REC_HEADER = struct.Struct('!L') # size of the record
    VERSION = 1

    def __init__(self, filename, record_count, record_size):
        '''Initializes an instance of PersistentQueue and the backing buffer file.'''

        self.filename = os.path.abspath(filename)
        self.record_count = record_count
        self.record_size = record_size + self.REC_HEADER.size

        # XXX: We should check if the buffer file params match file metadata
        self.open()

    def open(self):
        '''Creates/opens and initializes the buffer file.'''

        try:
            os.makedirs(os.path.dirname(self.filename))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass # Dir already exists
            else:
                raise
        
        try:
            # File does not exist
            fd = os.open(self.filename, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
            
            self.f = os.fdopen(fd, 'r+b', 0o600)

            self._allocate()
        except OSError as e:
            if e.errno == errno.EEXIST: # File exists
                self.f = open(self.filename, 'r+b', 0o600)
            else:
                raise
    
    def close(self):
        '''Closes the buffer file.'''

        self.f.close()

    def put(self, record):
        '''Puts a record into the queue.

        param record : byte string
            The record which will be put into the queue.

        Once this method returns, the record is guaranteed to be enqueued.
        '''

        assert len(record) <= self.record_size

        first_rec, last_rec = self._get_header()

        self._seek_to_record(last_rec)

        self.f.write(self.REC_HEADER.pack(len(record)))
        self.f.write(record)

        # In case of overflow, when there are records in the queue, overwrite the first (oldest) record
        if (last_rec % self.record_count) == (first_rec % self.record_count) and last_rec > first_rec:
            first_rec += 1

        self._set_header(first_rec, last_rec + 1)
        self.f.flush()

    def get(self):
        '''Returns the oldest records along with its ID.

        return (rec_id, record) : (long, byte string)

        Note: you must call the task_complete(rec) method after you are done
        processing the record. Otherwise, the same record will be returned
        again.
        '''

        first_rec, last_rec = self._get_header()
        
        if first_rec >= last_rec:
            return None, None

        self._seek_to_record(first_rec)
        
        length = self.REC_HEADER.unpack(self.f.read(self.REC_HEADER.size))[0]

        return first_rec, self.f.read(length)

    def task_complete(self, rec_id):
        '''Marks the record identified with rec_id as complete.

        Note that you must pass in the rec_id corresponding to the oldest record
        you retreived. If another thread/process called the get() method between
        your get() and task_complete(), an error will be raised. To avoid this,
        ue the lock() and unlock() methods of this class around your 
        get() and task_complete() code block.
        '''

        first_rec, last_rec = self._get_header()

        assert first_rec == rec_id
        self._set_header(rec_id + 1, last_rec)
        self.f.flush()

    def lock(self):
        '''Acquires an exclusive write lock on the queue.

        This method waits indefinitely to acquire the lock.
        '''

        fcntl.lockf(self.f, fcntl.LOCK_EX)

    def unlock(self):
        '''Unlocks the queue.'''

        fcntl.lockf(self.f, fcntl.LOCK_UN)

    def resize(self, new_record_count, new_record_size):
        '''Resizes the buffer file to the given spec.

        This method creates a copy of the buffer file, then copies records
        from it into the existing buffer file.
        '''

        # XXX: This should probably be a bit more atomic. Otherwise, if this
        # process is interrupted, we would lose some of the records.

        self.lock()

        # Make a copy to read data from
        tmp_fd, tmp_filename = tempfile.mkstemp(dir=os.path.dirname(self.filename))
        os.close(tmp_fd)

        shutil.copy2(self.filename, tmp_filename)
        q = PersistentQueue(tmp_filename, self.record_count, self.record_size - self.REC_HEADER.size)
        q.lock()

        self.record_count = new_record_count
        self.record_size = new_record_size + self.REC_HEADER.size

        self._allocate()

        while True:
            rec_id, record = q.get()
            if rec_id is None:
                break

            # Discard records that are too long, if new_record_size is shrinking
            if len(record) <= self.record_size:
                self.put(record)

            q.task_complete(rec_id)

        q.unlock()
        q.close()
        os.unlink(q.filename)

        self.unlock()

    def _set_header(self, first_rec, last_rec):
        '''Sets the current first and last record ID's.'''

        self.f.seek(0)
        self.f.write(self.FILE_HEADER.pack(self.VERSION, self.record_count, self.record_size, first_rec, last_rec))

    def _get_header(self):
        '''Returns the current first and last record ID's.'''

        self.f.seek(0)
        header = self.FILE_HEADER.unpack(self.f.read(self.FILE_HEADER.size))

        return header[-2:]

    def _allocate(self):
        '''Allocates a new file or re-initializes an existing file with self.record_count, self.record_size.'''

        self._set_header(0, 0)

        self.f.seek(self.record_count * self.record_size + self.FILE_HEADER.size - 1)
        self.f.write('\0')
        self.f.truncate()
        self.f.flush()
    
    def _seek_to_record(self, rec_id):
        '''Seeks to the location of the given rec_id in the buffer file.'''

        rec_pos = rec_id % self.record_count
        self.f.seek(rec_pos * self.record_size + self.FILE_HEADER.size)
