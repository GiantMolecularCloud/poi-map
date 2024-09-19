import logging
from typing import Sequence
import pprint
import sys

from .parser import parse_config
from ..io.database import get_data, get_markers
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

    # Prepare data
    df = get_data(config.database)
    markers = get_markers(df)

    # Run app
    poi_app = POIMapApp(config)
    poi_app.build(markers)
    poi_app.run()

    sys.exit(0)
