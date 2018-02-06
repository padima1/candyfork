#!/usr/bin/env python

# This script is meant to be used with bitcoin_fork_claimer: https://github.com/ymgve/bitcoin_fork_claimer
# The outputs of this script are the inputs to the other script.
# Python 2.x is required

import urllib2
import json
import sys

# Insert your BTC addresses, one per line
addresses = """
1HTmbaeSZn7faPjxcSeEHJoxgBGMxJYYem
15ZvPgCkTrkKsUzw8PaianK6W7sZQhTMK1
"""

# Forks to check. No need to touch, unless you want to add or remove a fork
fork_list = {
"BCD": { "name": "Bitcoin Diamond", "block": 495866 },
"SBTC": { "name": "Super Bitcoin", "block": 498888 },
"BTG": { "name": "Bitcoin Gold", "block": 491407 },
"B2X": { "name": "Segwit2x", "block": 501451 },
"BCX": { "name": "BitcoinX", "block": 498888 },
"BTP": { "name": "BitcoinPay", "block": 499345},
"BTF": { "name": "Bitcoin Faith", "block": 500000 },
"BPA": { "name": "Bitcoin Pizza", "block": 501888},
"BTH": { "name": "Bitcoin Hot", "block": 498848 },
"BTN": { "name": "Bitcoin New", "block": 501000 },
"BTW": { "name": "Bitcoin World", "block": 499777 },
"BTV": { "name": "Bitcoin Vote", "block": 505050 }
}

desired_forks = {}

def main():
	addr_list = addresses.strip().split("\n")

	global desired_forks
	desired_forks = get_desired_forks()
	if len(desired_forks) == 0:
		print "Retrieving all forks..."
		print
		desired_forks = fork_list

	for addr in addr_list:
		a = urllib2.urlopen("https://blockchain.info/rawaddr/" + addr).read()
		txs = json.loads(a)["txs"]

		for coincode, coindata in desired_forks.viewitems():
			valid = process_txs(addr, txs, coindata)
			for value in valid:
				if not coindata.has_key("commands"):
					coindata["commands"] = []
				coindata["commands"].append("python claimer.py " + coincode + " " + " ".join(value) + " " + coincode + "_ADDR")

	print_commands()

def process_txs(addr, txs, coin):
	txs_before_fork = [tx for tx in txs if tx.has_key("block_height") and tx["block_height"] <= coin["block"]]
	valid_txs = txs_before_fork[:]
	valid = []

	for txid in valid_txs[:]:
		for tx in txs_before_fork:
			for input_tx in tx["inputs"]:
				if input_tx["prev_out"]["tx_index"] == txid["tx_index"] and input_tx["prev_out"]["addr"] == addr:
					try:
						valid_txs.remove(txid)
					except ValueError:
						pass # Was probably removed before. Skipping.

	for tx in valid_txs:
		for tx_out in tx["out"]:
			if addr == tx_out["addr"]:
				valid.append([tx["hash"], "PRIV_KEY_OF_" + addr, addr])
				break

	return valid

def print_commands():
	for coincode, coindata in desired_forks.viewitems():
		if coindata.has_key("commands"):
			print coindata["name"] + " (" + coincode + ")"
			print "\n".join(coindata["commands"])
			print

def get_cli_args():
	if len(sys.argv) == 1:
		print "You can also specify which forks you want. Example: python " + sys.argv[0] + " btv bcx"
		return None

	return [arg.upper() for arg in sys.argv[1:]]

def get_desired_forks():
	cli_args = get_cli_args()
	if cli_args is None:
		return {}
	return {k : v for k, v in fork_list.iteritems() if k in cli_args}

main()
