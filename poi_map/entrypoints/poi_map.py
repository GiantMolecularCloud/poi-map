import logging
import pprint
import sys
from typing import Sequence

from ..app.app import POIMapApp
from .parser import parse_config

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


if __name__ == "__main__":
    main()
