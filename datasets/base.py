# ============================================================
# BaseDataset — Every dataset must inherit from this
# To add a new dataset:
#   1. Create a new file in datasets/
#   2. Inherit from BaseDataset
#   3. Implement get_log()
#   4. Register in datasets/utils.py
# ============================================================

class BaseDataset:

    def get_log(self):
        """
        Returns one raw log line as a string.
        Called repeatedly by the pipeline.
        """
        raise NotImplementedError

    def name(self):
        """
        Returns dataset name e.g. "synthetic"
        Must match the key in datasets/utils.py
        """
        raise NotImplementedError

    def description(self):
        """
        Human readable description of this dataset.
        """
        raise NotImplementedError
