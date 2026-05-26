import pickle


class ImportListener:
    def load_course(self, raw_bytes):
        # VULNERABILITY A08: Untrusted pickle payload is deserialized without class restrictions.
        return pickle.loads(raw_bytes)
