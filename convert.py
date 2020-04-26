#!/usr/bin/env python3
import glob
import argparse
import csv
import datetime
from os import path
from dataclasses import dataclass, asdict
from decimal import Decimal
import logging

from bs4 import BeautifulSoup


CHARSET = "shift_jisx0213"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass(eq=True, frozen=True)
class Entry:
    """Contain a single GAICA entry."""

    date: datetime.date
    memo: str
    amount: Decimal
    fee: Decimal
    atm_fee: Decimal
    conversion_fee: Decimal
    decision: str
    tx_id: int
    note: str


def clean_decimal(raw, allow_null=False):
    """Return a decimal from a number of format X,XXX.XX."""
    cleaned = raw.strip().replace(',', '')
    if cleaned:
        return Decimal(cleaned)
    if allow_null:
        return Decimal(0)
    raise ValueError(f"Did not know how to handle {raw}")


def read_in(fd):
    """Read HTML table from file and output entries."""
    contents = fd.read()
    soup = BeautifulSoup(contents, features="html.parser")
    table = soup.find("table")
    trs = table.find_all("tr")

    entries = set()
    for index, row in enumerate(trs):
        if row.find_all("th"):
            continue
        date, *_ = row.find_all("td")
        if not (date.string and date.string.strip()):
            continue

        tds = row.find_all("td")
        date_raw = tds[0].string.strip()
        amount_raw = tds[2].find_all("div")[1].string.strip()
        memo = tds[1].string.strip()
        amount = clean_decimal(amount_raw)
        if memo == "チャージ":
            amount *= -1

        entry = Entry(
            date=datetime.date.fromisoformat(date_raw.replace("/", "-")),
            memo=memo,
            amount=amount,
            fee=clean_decimal(tds[3].string, allow_null=True),
            atm_fee=clean_decimal(tds[4].string, allow_null=True),
            conversion_fee=clean_decimal(tds[5].string, allow_null=True),
            decision=tds[6].string.strip(),
            tx_id=tds[7].string.strip(),
            note=tds[8].string.strip(),
        )

        entries.add(entry)
    return entries


def main(args):
    """
    Main method.

    1) Read in all html files in input_folder
    2) Return if nothing was read in
    3) Write contents to csv file
    """
    # Expected YYYY/MM/NO.html
    gl = path.join(args.input_folder, "*/*/*.html")
    contents = set()
    for file in glob.glob(gl):
        logger.info("Reading in %s", file)
        with open(file, encoding=CHARSET) as fd:
            contents.update(read_in(fd))

    if not contents:
        logger.info("Nothing was read in")
        return
    logger.info("%d rows were read in total", len(contents))

    logger.info("Writing to %s", args.output)

    with open(args.output, 'w') as fd:
        writer = csv.DictWriter(
            fd,
            asdict(next(iter(contents))).keys(),
        )
        writer.writeheader()
        for row in contents:
            writer.writerow(asdict(row))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_folder")
    parser.add_argument("output")
    args = parser.parse_args()
    main(args)
