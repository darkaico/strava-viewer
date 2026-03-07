from strava_viewer.utils import logger_utils


class LoggerMixin:

    _logger = None
    logger_name = None

    @property
    def logger(self):
        if not self._logger:
            logger_name = self.logger_name
            if not logger_name:
                logger_name = self.__class__.__name__.lower()

            self._logger = logger_utils.build_logger(logger_name)

        return self._logger
