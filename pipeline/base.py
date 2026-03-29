# ============================================================
# BasePipeline — Every pipeline must inherit from this
# To add a new pipeline:
#   1. Create a new file in pipeline/
#   2. Inherit from BasePipeline
#   3. Implement run() and stop()
#   4. Register in pipeline/utils.py
# ============================================================


class BasePipeline:

    def run(self, dataset, preprocessor, model, storage):
        """
        Main pipeline loop.
        Connects dataset → preprocessor → model → storage.
        Runs until stop() is called.
        """
        raise NotImplementedError

    def stop(self):
        """Stops the pipeline gracefully."""
        raise NotImplementedError

    def name(self) -> str:
        raise NotImplementedError

    def description(self) -> str:
        raise NotImplementedError
