from p2pnetwork.node import Node
from wof_pb2 import *

from enum import IntEnum

class MessageType(IntEnum):
	ORDER_AGREEMENT = 0

class State(IntEnum):
	INIT = 0
	CONNECTED = 1
	ORDER_AGREED = 2

class WOFNode (Node):

	# host must be a string
	# port must be a number
	# players must be an array of tuples (host, port)
	def __init__(self, host, port, players):
		super(WOFNode, self).__init__(host, port, None)
		self.players = players
		self.advance_state(State.INIT)

	##################################################
	# State machine methods

	# Advances the state and executes the next stage
	def advance_state(self, state):
		self.state = state
		if self.state == State.INIT:
			print("WOFNode: Started")
			self.connect_to_players()
		elif self.state == State.CONNECTED:
			print("connected to all the other players")
			self.agree_order()
		elif self.state == State.ORDER_AGREED:
			print("all players agreed on the order")

	# First stage after loading this server: try to connect to the other players.
	def connect_to_players(self):
		for p in self.players:
			self.connect_with_node(p[0], p[1])

	# Second stage, compute the order of the players and send agreement messages.
	def agree_order(self):
		p = PlayerOrder()
		p.id.extend(self.player_order)
		self.orderAgreed = {}
		self.send_typed_msg_to_nodes(MessageType.ORDER_AGREEMENT, p.SerializeToString())

	##################################################
	# Reactive methods

	# Check whether all players are connected.
	def check_connections(self):
		if len(self.all_nodes) == len(self.players):
			self.advance_state(State.CONNECTED)
		elif len(self.all_nodes) > len(self.players):
			raise Exception("Connected to too many players.")

	# Check whether all players agreed on the player order.
	def check_order_agreement(self, nodeId, order):
		if nodeId in self.orderAgreed:
			return

		if order != self.player_order:
			print("Node " + str(nodeId) + " sent a different player order: " + str(order))
			return

		self.orderAgreed[nodeId] = True
		if len(self.orderAgreed) == len(self.all_nodes):
			self.advance_state(State.ORDER_AGREED)

	##################################################
	# Helper methods

	# Add message type as the first byte of the message and send message.
	def send_typed_msg_to_nodes(self, msg_type, data):
		self.send_to_nodes(msg_type.to_bytes(1, byteorder='big') + data)

	# Compute the player order based on their node ids.
	@property
	def player_order(self):
		return sorted([n.id for n in self.all_nodes] + [self.id])

	##################################################
	# Message parsing methods

	# Node that initiated connection request.
	def parse_outbound_node_connected(self, node):
		print("outbound_node_connected: " + node.id)
		self.check_connections()

	# Node that received connection request.
	def parse_inbound_node_connected(self, node):
		print("inbound_node_connected: " + node.id)
		self.check_connections()

	# Node received an order agreement request.
	def parse_order_agreement(self, nodeId, data):
		p = PlayerOrder()
		p.ParseFromString(data)
		self.check_order_agreement(nodeId, p.id)

	##################################################
	# Network related methods

	# Every received message comes here.
	def node_message(self, node, data):
		print("node_message from " + node.id + ": " + str(data))
		t = data[0]
		if t == MessageType.ORDER_AGREEMENT:
			self.parse_order_agreement(node.id, data[1:])
		else:
			raise Exception("Received unknown message type.")

	def outbound_node_connected(self, node):
		self.parse_outbound_node_connected(node)

	def inbound_node_connected(self, node):
		self.parse_inbound_node_connected(node)

	def inbound_node_disconnected(self, node):
		print("inbound_node_disconnected: " + node.id)

	def outbound_node_disconnected(self, node):
		print("outbound_node_disconnected: " + node.id)

	def node_disconnect_with_outbound_node(self, node):
		print("node wants to disconnect with oher outbound node: " + node.id)

	def node_request_to_stop(self):
		print("node is requested to stop!")
