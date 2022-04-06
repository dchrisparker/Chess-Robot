# By Chris Parker 8/26/21

class Node:
    def __init__(self, data, next_node=None, previous_node=None):
        self.data = data
        self.next : Node
        self.previous : Node
        self.next = next_node
        self.previous = previous_node

    def __str__(self):
        next_data = None
        prev_data = None

        if self.next:
            next_data = self.next.data
        if self.previous:
            prev_data = self.previous.data

        return f"{self.data} | {next_data}, {prev_data}"

class DoubleLinkedList:
    def __init__(self, *data):
        """Create a new DoubleLinkedList"""
        self._index = 0 # Current location in list

        self.head = None # Start
        self.tail = None # End
        self.len = 0

        self.current: Node = None # Working node

        if data:
            self.add_start(data[0])
            self.len += 1
            if len(data) > 1:
                for datum in data[1:]:
                    #print(datum)
                    self.add_end(datum)
                    self.len += 1

    def add_start(self, data):
        """Add an item to the start of the list

        Parameters
        ----------
        data : Any
            The data to put in the node
        """
        node = Node(data)

        if self.head:
            node.next = self.head
            self.head.previous = node
            self.head = node
        else:
            self.head = node
            self.current = node
            if self.tail == None:
                self.tail = node

        self._index += 1
        self.len += 1


    def add_end(self, data):
        """Add an item to the end of the list

        Parameters
        ----------
        data : Any
            The data to put in the node
        """
        node = Node(data)

        if self.tail != None:
            node.previous = self.tail
            self.tail.next = node
            self.tail = node
        else:
            if self.head == None:
                self.head = node
                self.current = node

            self.tail = node

        self.len += 1
            
    def next(self) -> Node:
        """Move to the next item

        Returns
        -------
        Node
            The current node after moving
        """
        if self.current.next:
            self._index += 1
            self.current = self.current.next
        return self.current or False 

    def previous(self) -> Node:
        """Move to the previous item

        Returns
        -------
        Node
            The current node after moving
        """
        if self.current.previous:
            self._index -= 1
            self.current = self.current.previous
        return self.current or False

    def pop(self) -> Node:
        """Remove an item from the end of the list and return it

        Returns
        -------
        Node
            Popped node
        """
        rtn = self.tail

        self.tail = self.tail.previous
        self.tail.next = None

        self.len -= 1

        return rtn or False

    def add_node(self, data, index: int) -> bool:
        """Add a node at an arbitrary index
        NOTE: Do not use this for the first or last item!

        Parameters
        ----------
        data : Any
            The data to put in the node
        index : int
            Index where the node will be after insertion
        """
        if index == 0:
            self.add_start(data)
            return True
        
        start = self._index
        new_node = Node(data) # Step 1

        self.move_to_index(index-1) # Step 2

        new_node.previous = self.current # Step 3
        new_node.next = new_node.previous.next # Step 4
        self.current.next = new_node # Step 5
        new_node.next.previous = new_node # Step 6

        self.move_to_index(start) # Returning to the original position

        self.len += 1
        
        return True

    def move_to_index(self, index: int):
        """Move the current node reference to an arbitrary index

        Parameters
        ----------
        index : int
            Index to move to
        """
        diff = index - self._index

        if diff > 0:
            for i in range(diff):
                #print("f")
                self.next()
        elif diff < 0:
            for i in range(-diff):
                #print("b")
                self.previous()

    def remove_first(self) -> Node:
        """Remove 1st item in list and return it.

        Returns
        -------
        Node
            Node removed
        """
        rtn = self.head
        self.head = self.head.next
        self.head.previous = None
        
        self.len -= 1
        
        return rtn
    
    def remove_last(self) -> Node:
        """Remove last item in list and return it.

        Returns
        -------
        Node
            Node removed
        """
        return self.pop()

    def remove_node(self, node: Node):
        """Remove given node.

        Parameters
        ----------
        node : Node
            Node to remove
        """
        node.previous.next = node.next
        node.next.previous = node.previous
        
        node.next, node.previous = None, None
    
    def remove_index(self, index: int) -> Node:
        """Remove node at given index and return it.

        Parameters
        ----------
        index : int
            Index to delete
            
        Returns
        -------
        Node
            Node removed
        """
        prev_index = self._index
        if prev_index > index:
            prev_index -= 1
        
        self.move_to_index(index)
        
        self.remove_node(self.current)
        
        self.move_to_index(prev_index)
    
    def reset_index(self):
        self._index = 0
    
    def _count_len(self):
        self.current = self.head
        new_len = 1
        while self.current.next:
            new_len += 1
            self.current = self.current.next
            
        self.len = new_len
            

    def __len__(self) -> int:
        return self.len

    def __str__(self) -> str:
        rtn = ""

        start = self._index
        self.move_to_index(0)
        while self.current.next:
            rtn += str(self.current)
            self.next()
            rtn += "; "
        rtn += str(self.tail)

        self.move_to_index(start)

        return rtn
        
## Fun functions
def reverse_dll(l : DoubleLinkedList):
    temp_node : Node
    c_node = l.head

    while c_node != None:
        temp_node = c_node.next
        c_node.next = c_node.previous
        c_node.previous = temp_node

        if c_node.previous:
            c_node = c_node.previous
        else:
            c_node = None
        
def main():
    llist = DoubleLinkedList("A", "C", "D") # Create a new list containing these values

    print(llist)

    llist.add_start("A*") # Add "A*" to the front
    llist.add_end("D*") # Add "D*" to the back

    print(llist)

    print("Popped:", llist.pop()) # Pop an item from the end

    llist.add_node("B", 1) # Add "B" between "A*" & "A"

    print(llist)

    reverse_dll(llist)

    print(llist)

if __name__ == "__main__":
    main()

### OUTPUT
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                               #
# A | C, None; C | D, A; D | None, C                            #
# A* | A, None; A | C, A*; C | D, A; D | D*, C; D* | None, D    #
# Popped: D* | None, D                                          #
# A* | B, None; B | A, A*; A | C, B; C | D, A; D | None, C      #
#                                                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #