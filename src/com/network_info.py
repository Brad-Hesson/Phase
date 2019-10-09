import time
from src.com import Node

node = Node('network_info')
node.register_node()

time.sleep(1)

print('Nodes:')
for n in node.nodes:
    print(' - ' + str(n))
print('')

print('Streaming Channels:')
for topic in node.channels.keys():
    print(' - ' + str(topic))
print('')

print('State Topics:')
for topic in node.topics.keys():
    print(' - ' + str(topic))
