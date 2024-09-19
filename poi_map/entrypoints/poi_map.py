import logging
from typing import Sequence
import pprint
import sys

from .parser import parse_config
from ..app.app import POIMapApp

log = logging.getLogger(__name__)


def main(argv: Sequence[str] | None = None) -> None:
    config = parse_config(argv)

    logging.basicConfig(
        format="[%(asctime)s] [%(levelname)8s] --- %(message)s",
        level=config.loglevel,
    )

    log.info("-" * 50)
    log.info("Config successfully parsed.")
    for line in pprint.pformat(config).split(", "):
        log.info(line)
    log.info("-" * 50)

    # Run app
    poi_app = POIMapApp(config)
    poi_app.build()
    poi_app.run()

    sys.exit(0)
