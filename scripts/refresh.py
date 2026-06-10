"""Course-facing entrypoint for the async IOC refresh worker."""

import asyncio
import logging

from worker.refresh import run


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    added, skipped = asyncio.run(run())
    print(f"Refresh complete: {added} added, {skipped} skipped.")
