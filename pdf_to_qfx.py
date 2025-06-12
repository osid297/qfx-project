import argparse
import pdfplumber
import re
from datetime import datetime
from typing import List, Tuple


TRANSACTION_PATTERN = re.compile(r"(\d{2}/\d{2})\s+(.*?)\s+(-?\d+\.\d{2})$")

def parse_pdf_transactions(pdf_path: str) -> List[Tuple[datetime, str, float]]:
    """Extract transactions from a credit-card statement PDF."""
    text_lines = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text_lines.extend(extracted.splitlines())
    transactions = []
    current_year = datetime.now().year
    for line in text_lines:
        match = TRANSACTION_PATTERN.search(line)
        if match:
            date_str, memo, amount_str = match.groups()
            # Append current year to date for parsing
            date = datetime.strptime(f"{date_str}/{current_year}", "%m/%d/%Y")
            amount = float(amount_str.replace(',', ''))
            transactions.append((date, memo.strip(), amount))
    return transactions

def generate_qfx(transactions: List[Tuple[datetime, str, float]], account_id: str = "0000", bank_id: str = "000000000") -> str:
    """Return a QFX string for the given transactions."""
    header = (
        "OFXHEADER:100\n"
        "DATA:OFXSGML\n"
        "VERSION:102\n"
        "SECURITY:NONE\n"
        "ENCODING:USASCII\n"
        "CHARSET:1252\n"
        "COMPRESSION:NONE\n"
        "OLDFILEUID:NONE\n"
        "NEWFILEUID:NONE\n\n"
    )
    ofx_open = "<OFX>\n  <BANKMSGSRSV1>\n    <STMTTRNRS>\n      <STMTRS>\n        <BANKACCTFROM>\n          <BANKID>{bank_id}</BANKID>\n          <ACCTID>{acct_id}</ACCTID>\n          <ACCTTYPE>CREDITLINE</ACCTTYPE>\n        </BANKACCTFROM>\n        <BANKTRANLIST>\n".format(bank_id=bank_id, acct_id=account_id)
    ofx_close = (
        "        </BANKTRANLIST>\n      </STMTRS>\n    </STMTTRNRS>\n  </BANKMSGSRSV1>\n</OFX>\n"
    )
    txn_lines = []
    for idx, (date, memo, amount) in enumerate(transactions, 1):
        txn_lines.append(
            "          <STMTTRN>\n"
            f"            <TRNTYPE>OTHER</TRNTYPE>\n"
            f"            <DTPOSTED>{date.strftime('%Y%m%d')}</DTPOSTED>\n"
            f"            <TRNAMT>{amount:.2f}</TRNAMT>\n"
            f"            <FITID>{idx}</FITID>\n"
            f"            <NAME>{memo}</NAME>\n"
            "          </STMTTRN>\n"
        )
    return header + ofx_open + "".join(txn_lines) + ofx_close

def main() -> None:
    parser = argparse.ArgumentParser(description="Convert credit-card statement PDF to QFX")
    parser.add_argument("pdf", help="Input PDF statement")
    parser.add_argument("output", help="Output QFX file")
    parser.add_argument("--account-id", default="0000", help="Account ID for QFX")
    parser.add_argument("--bank-id", default="000000000", help="Bank ID for QFX")
    args = parser.parse_args()

    txns = parse_pdf_transactions(args.pdf)
    qfx_content = generate_qfx(txns, account_id=args.account_id, bank_id=args.bank_id)
    with open(args.output, "w") as f:
        f.write(qfx_content)

if __name__ == "__main__":
    main()
