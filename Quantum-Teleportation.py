from projectq.ops import CNOT, H, Measure, X, Z
from projectq import MainEngine

def entangled_pair(engine):
    # Initializing two qubits.
    # qubit one will be used by sender to create message 
    qubit_one = engine.allocate_qubit()
    # quibit two will be used by receiver to reproduce the message
    qubit_two = engine.allocate_qubit()
    
    # Hadamard gate, putting first qubit in superposition of the two eigenstates
    # Equal prob of measuring |0> or |1>
    H | qubit_one

    # CNOT gate to make one bit flip conditionally to the other
    # This ensures that our two bits are indeed a bell pair. 
    # i.e., we have two possible states; if one bit is in a state,
    # the other will be in the only other possible state
    CNOT | (qubit_one, qubit_two)
    return qubit_one, qubit_two


def create_message(engine = '', qubit_one='', msg_value = 0):
    # Entangle message
    qubit_to_send = engine.allocate_qubit()

    # Pauli X gate to flip qubit
    if msg_value == 1:
        X | qubit_to_send

    #Entangling message qubit with qubit_one
    CNOT | (qubit_to_send, qubit_one)
    
    # Putting message qubit in superposition
    H | qubit_to_send
    # Collapsing states
    Measure | qubit_to_send
    Measure | qubit_one
    # Now there are four possibilities the encoded_msg:
    # 00, 01, 10, 11
    # Each with probability 1/4
    encoded_msg= [int(qubit_to_send), int(qubit_one)]
    return encoded_msg

def receiver(engine, msg, qubit_two):
    # To decode every received bit:
    # If second bit is 1, apply X gate to receiver's own qubit
    # to recover sender's qubit info
    # If first bit is 0, apply Z gate to receiver's own qubit
    # to recover sender's qubit info
    if msg[1] == 1:
        X | qubit_two  # like a classical bit flip gate
    if msg[0] == 1:
        Z | qubit_two  # Z gates leaves |0> states unchanged but flips |1> to |0>
    
    # Collapsing states
    Measure | qubit_two
    engine.flush()
    bit = int(qubit_two)
    return bit

def send_return(bit = 0, engine =''):
    # Create entangled pair
    qubit_one, qubit_two = entangled_pair(engine)
    encoded_msg = create_message(engine = engine, qubit_one = qubit_one, msg_value = bit )
    # Teleport to the receiver bit and returning the bit he believes
    # was the sender's bit
    # If this returns the same bit as the sent bit, teleportation worked!
    return receiver(engine, encoded_msg, qubit_two)

def send_msg(msg = 'Quantum Physics is awesome', engine = ''):
    binary_encoded_msg = [bin(ord(x))[2:].zfill(8) for x in msg]
    print('Message sent: ', msg)
    print('Binary message sent: ', binary_encoded_msg)
    
    received_bytes_list = []
    # Applying the `receive` method on every bit of the message
    for letter in binary_encoded_msg:
        received_bits = ''
        for bit in letter:
            received_bits = received_bits +  str(send_return(int(bit), engine))
        received_bytes_list.append(received_bits)
    binary_to_string = ''.join([chr(int(x,2)) for x in received_bytes_list])
    print('Received Binary Message: ', received_bytes_list)
    print('Received Message: ', binary_to_string)
    
    

# Main compiler engine
engine = MainEngine()
msg = 'Einstein - Podolsky - Rosen'
send_msg(msg = msg, engine = engine)

    



