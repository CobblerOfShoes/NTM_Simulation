import argparse
import copy
import os
import csv
import sys
from collections import defaultdict, Counter

class Tape():
  def __init__(self, tapeString="", blankSymbol="_"):
    # We use a dict and not an array so we can more easily lengthen the tape
    self.__blank_symbol = blankSymbol
    tape_dict = dict(enumerate(tapeString))
    self.__tape = defaultdict(lambda: self.__blank_symbol)
    for key, value in tape_dict.items():
      self.__tape[key] = value

  def getLeftOfCharacter(self, index):
    if index in self.__tape:
      s = ""
      for i in range(index):
        s += self.__tape[i]
      return s
    else:
      return str(self)
    
  def getRightOfCharacter(self, index):
    if index in self.__tape:
      s = ""
      for i in range(index+1, len(self.__tape)):
        s += self.__tape[i]
      return s
    else:
      return self.__blank_symbol

  def getCharacter(self, index):
    if index in self.__tape:
      return self.__tape[index]
    else:
      return self.__blank_symbol
    
  def setCharacter(self, index, char):
    if index in self.__tape:
      self.__tape[index] = char
    else:
      self.__tape.update({index: char})

  def __str__(self):
    s = ""
    topCharIndex = min(self.__tape.keys())
    endCharIndex = max(self.__tape.keys())
    for i in range(topCharIndex, endCharIndex+1):
      s += self.__tape[i]
    return s

class NTM_Transition():
  def __init__(self,
               new_state: str,
               new_character: str,
               direction: str):
    self.new_state: str = new_state
    self.new_character: str = new_character
    self.direction: str = direction

class NTM_Configuration():
  def __init__(self,
               tape: Tape,
               head_position: int,
               current_state: str,
               previous_states: list = [],
               depth: int = 0):
    self.tape = tape
    self.head_position = head_position
    self.current_state = current_state
    self.previous_states = previous_states
    self.depth = depth

  def getHeadCharacter(self):
    return self.tape.getCharacter(self.head_position)
  
  def getLeftOfHead(self):
    return self.tape.getLeftOfCharacter(self.head_position)
  
  def getRightOfHead(self):
    return self.tape.getRightOfCharacter(self.head_position)

class NTM():
  def __init__(self,
               initial_state,
               accept_state,
               reject_state,
               transition_function,
               max_depth = 100,
               blank_symbol = "_",):
    # Keep a counter to prevent infinite loops
    self.__max_depth = max_depth
    # Keep a boolean to check if we are within depth
    self.__searching = True

    self.__blank_symbol: str = blank_symbol
    self.__initial_state = initial_state
    self.__transition_function: dict[tuple: list[NTM_Transition]] = transition_function
    self.__accept_state = accept_state
    self.__reject_state = reject_state
    # Create a queue to hold available transitions
    self.__next_configurations: list[NTM_Configuration] = []
    self.__nondeterminism = Counter()
  
  # Returns a list of possible transitions available from a given state and input
  def __get_transitions(self, current_state, current_char):
    # transitions = self.__transition_function[(current_state, current_char)]
    # # If no transition available, assume it goes to the reject state
    # if transitions == []:
    #   return [(self.__reject_state, current_char, 'R')]
    # return transitions

    
    try:
      return self.__transition_function[(current_state, current_char)]
    # If no transition available, assume it goes to the reject state
    except IndexError:
      return [(self.__reject_state, current_char, 'R')]

  def __accept(self, final_config: NTM_Configuration):
    print()
    print(f"String accepted in {final_config.depth} transitions.")
    total_transitions = sum(self.__nondeterminism.values())
    print(f"Total number of transitions simulated: {total_transitions}")
    avg_nondeterminism = total_transitions / len(self.__nondeterminism)
    print(f"Average non-determinism: {avg_nondeterminism}")
    print("")
    print(f"--- Configuration History ---")
    for config in final_config.previous_states:
      print(f"Left of head: {config.getLeftOfHead()} | " + \
            f"State: {config.current_state} | " + \
            f"Head Character: {config.getHeadCharacter()} | " + \
            f"Right of head: {config.getRightOfHead()}")      

  def __reject(self, final_config: NTM_Configuration):
    print()
    print(f"String rejected in {final_config.depth} transitions.")
    total_transitions = sum(self.__nondeterminism.values())
    print(f"Total number of transitions simulated: {total_transitions}")
    avg_nondeterminism = total_transitions / len(self.__nondeterminism)
    print(f"Average non-determinism: {avg_nondeterminism}")

  def __apply_transition(self, configuration: NTM_Configuration, transition: NTM_Transition):
    new_configuration: NTM_Configuration = copy.deepcopy(configuration)
    new_configuration.current_state = transition.new_state
    new_configuration.tape.setCharacter(new_configuration.head_position, transition.new_character)
    direction = transition.direction.upper()
    if direction == "R":
      new_configuration.head_position += 1
    else:
      new_configuration.head_position -= 1
    new_configuration.previous_states.append(configuration)
    new_configuration.depth += 1
    return new_configuration

  # Get all the possible next states from the state at the top of the queue
  def __step(self, verbose):
    next_configuration = self.__next_configurations.pop()

    # Set a max depth to avoid infinite recursion
    if next_configuration.depth >= self.__max_depth:
      self.__searching = False
      print()
      print(f"ERROR: Maximum traversal depth of {self.__max_depth} exceeded.")
      sys.exit(1)

    # Print out intermediary steps
    if verbose:
      print(f"Left of head: {next_configuration.getLeftOfHead()} | " + \
            f"State: {next_configuration.current_state} | " + \
            f"Head Character: {next_configuration.getHeadCharacter()} | " + \
            f"Right of head: {next_configuration.getRightOfHead()} | " + \
            f"Depth: {next_configuration.depth}")

    # Increment the nondeterminism counter
    self.__nondeterminism[next_configuration.depth] += 1

    # Check end cases
    if next_configuration.current_state == self.__accept_state:
      self.__searching = False
      self.__accept(next_configuration)

    elif next_configuration.current_state == self.__reject_state:
      self.__searching = False
      self.__reject(next_configuration)

    choices: NTM_Transition = self.__get_transitions(next_configuration.current_state, next_configuration.getHeadCharacter())

    # Generate next configurations from available transitions

    available_transitions = [self.__apply_transition(next_configuration, choice) for choice in choices]

    self.__next_configurations.extend(available_transitions)
    
  def set_depth(self, new_depth: int):
    self.__max_depth = new_depth

  def solve(self, tape: str, verbose):
    # Construct first transition
    starting_configuration = NTM_Configuration(Tape(tape), 0, self.__initial_state)
    self.__next_configurations.append(starting_configuration)

    if verbose:
      print()
      print("--- Intermediary Steps ---")

    while self.__searching:
      next_configuration = self.__step(verbose)

def parseMachineFile(filepath):
  with open(filepath, 'r') as machinefile:
    machinereader = csv.reader(machinefile, delimiter=',')

    # Print out the machine name
    machinename = next(machinereader)[0]
    print(f"Machine: {machinename}")

    # Ignore the list of states
    next(machinereader)

    # Ignore the input alphabet
    next(machinereader)

    # Ignore the write alphabet
    next(machinereader)

    # Grab the stuff we care about
    initial_state = next(machinereader)[0]
    accept_state = next(machinereader)[0]
    reject_state = next(machinereader)[0]

    # Build the transition function
    transition_function = defaultdict(list)
    for row in machinereader:
      try:
        new_transition = NTM_Transition(row[2], row[3], row[4])
        transition_function[(row[0], row[1])].append(new_transition)
      except IndexError:
        print(f"ERROR: Incomplete transition function in file {filepath}")

  # Compile the machine together
  return NTM(initial_state, accept_state, reject_state, transition_function)

def main():
  parser = argparse.ArgumentParser(usage="Pass an NTM machine description file and one or more strings to test. " +
                                         "Non-deterministacally checks for the fastest route to accept the string if one exists.")
  parser.add_argument("-d", dest="max_depth", required=False, type=int, default=100,
                      help="Maximum depth (int) that the NTM will search before giving up. Defaults to 100.")
  parser.add_argument("-f", dest="filename", required=True, type=str,
                      help="Input file NTM description.",
                      metavar="FILE")
  parser.add_argument("-s", dest="input_strings", required=True, type=str, nargs='+',
                      help="String to test on NTM.")
  parser.add_argument("-v", "--verbose", dest="verbose", required=False, action="store_true",
                      help="Toggles logging of intermediary configurations in NTM search.")
  
  args = parser.parse_args()

  # Test each file and each string
  for string in args.input_strings:
    filepath = os.path.abspath(args.filename)
    ntm = parseMachineFile(filepath)
    ntm.set_depth(args.max_depth)
    ntm.solve(string, args.verbose)


if __name__ == '__main__':
  main()