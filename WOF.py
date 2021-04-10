from WOFNode import WOFNode

import sys

if __name__ == '__main__':
	ip = sys.argv[1]
	port = int(sys.argv[2])
	players = []
	for i in range(3, len(sys.argv), 2):
		players.append((sys.argv[i], int(sys.argv[i + 1])));

	node = WOFNode(ip, port, players)
	node.run()
