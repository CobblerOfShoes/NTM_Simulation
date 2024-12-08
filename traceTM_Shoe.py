import argparse
import os
import csv
from collections import defaultdict

class Tape():
  blank_symbol = "_"

  def __init__(self, tapeString=""):
    self.__tape = dict(enumerate(tapeString))

  def getItem(self, index):
    if index in self.__tape:
      return self.__tape[index]
    else:
      return Tape.blank_symbol
    
  def setItem(self, index, char):
    self.__tape[index] = char

  def __str__(self):
    s = ""
    topCharIndex = min(self.__tape.keys())
    endCharIndex = max(self.__tape.keys())
    for i in range(topCharIndex, endCharIndex):
      s += self.__tape[i]
    return s

class NTM_Configuration():
  def __init__(self,
               current_state = "",
               depth = 0,
               previous_states = None):
    pass

class NTM():
  def __init__(self,
              #  tape = "",
               blank_symbol = "_",
               initial_state = "",
               final_states = None,
               transition_function = None,
               max_depth = 100):
    # self.__tape = Tape(tape)
    self.__head_position: int = 0
    self.__blank_symbol: str = blank_symbol
    self.__current_state = initial_state
    # Keep a queue for doing a BFS through the NTM
    self.__available_transitions = [self.__currentState]
    # Keep a counter to prevent infinite loops
    self.__max_depth = max_depth
    if transition_function == None:
      self.__transition_function = {}
      print("ERROR: No transition function detected.")
    else:
      self.__transition_function = transition_function
    if final_states == None:
      self.__final_states = set()
      print("ERROR: No final states given.")
    else:
      self.__final_states = set(final_states)

  def getTape(self):
    return self.__tape
  
  def getCurrentTapeChar(self):
    return self.__tape.getItem(self.__head_position)
  
  # Get all the possible next states from the state at the top of the queue
  def step(self):
    next_transition = self.__available_transitions.pop()

    # Set a max depth to avoid infinite recursion
    if next_transition.depth >= self.__max_depth:
      print(f"ERROR: Maximum traversal depth () exceeded.")
    


  def solve(self, tape: str):
    # Construct first transition
    starting_configuration = (self.__currentState)
    self.__tape = Tape(tape)

def parseMachineFile(filepath):
  with open(filepath, 'r') as machinefile:
    machinereader = csv.reader(machinefile, delimiter=',')

    # Print out the machine name
    machinename = next(machinereader)
    print(f"Machine: {machinename}")

    # Ignore the list of states
    next(machinereader)

    # Ignore the input alphabet
    next(machinereader)

    # Ignore the write alphabet
    next(machinereader)

    # Grab the stuff we care about
    initial_state = next(machinereader)
    print(initial_state, type(initial_state))
    accept_state = next(machinereader)
    print(accept_state, type(accept_state))
    reject_state = next(machinereader)

    # Build the transition function
    transition_function = defaultdict(list)
    for row in machinereader:
      try:
        transition_function[(row[0], row[1])].append( (row[2], row[3], row[4]) )
      except IndexError:
        print(f"ERROR: Incomplete transition function in file {filepath}")

  # Compile the machine together
  return NTM(initial_state=initial_state, final_states=reject_state, transition_function=transition_function)

def main():
  parser = argparse.ArgumentParser(usage="Pass an NTM machine description file and one or more strings to test. " +
                                         "Non-deterministacally checks for the fastest route to accept the string if one exists.")
  parser.add_argument("-t", dest="max_depth", required=False, type=int,
                      help="Maximum depth (int) that the NTM will search before giving up.")
  parser.add_argument("-f", dest="filename", required=True, nargs=1,
                      help="Input file NTM description.",
                      metavar="FILE")
  parser.add_argument("-s", dest="input_strings", required=True, nargs='+',
                      help="String to test on NTM.")
  
  args = parser.parse_args()

  # Test each file and each string
  for string in args.input_strings:
    filepath = os.path.abspath(args.filename)
    ntm = parseMachineFile(filepath)
    return
    ntm.solve(string)


if __name__ == '__main__':
  main()