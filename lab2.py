class BPlusTreeNode:
    def __init__(self, is_leaf=False):
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []
        self.next = None  

class BPlusTree:
    def __init__(self, order=4):
        self.root = BPlusTreeNode(is_leaf=True)
        self.order = order
    
    def map_letter_to_digit(self, letter):
        mapping = {
            'A': 1, 'B': 1, 
            'C': 2, 'D': 2, 'E': 2, 'F': 2, 'G': 2, 
            'H': 3, 'I': 3, 'J': 3, 'K': 3, 'L': 3, 'M': 3,
            'N': 4, 'O': 4, 'P': 4, 'Q': 4, 'R': 4, 'S': 4, 'T': 4, 'U': 4,
            'V': 5, 'W': 5, 'X': 5, 'Y': 5, 'Z': 5
        }
        return mapping.get(letter.upper(), 0)  
    
    def hash_name(self, name):
        name = name.upper()  
        hash_code = ""
        
        for i in range(min(3, len(name))):
            letter = name[i]
            digit = self.map_letter_to_digit(letter)
            hash_code += str(digit)
        
        hash_code = hash_code.ljust(7, '0')
        
        return int(hash_code)
    
    def insert(self, name, phone):
        key = self.hash_name(name)
        root = self.root
        
        if len(root.keys) == self.order - 1:
            new_root = BPlusTreeNode()
            new_root.children.append(self.root)
            self.split_child(new_root, 0)
            self.root = new_root
        
        self._insert_non_full(self.root, key, (name, phone))
    
    def split_child(self, parent, index):
        node = parent.children[index]
        mid = len(node.keys) // 2
        new_node = BPlusTreeNode(is_leaf=node.is_leaf)
        
        parent.keys.insert(index, node.keys[mid])
        parent.children.insert(index + 1, new_node)
        
        new_node.keys = node.keys[mid + 1:]
        node.keys = node.keys[:mid]
        
        if node.is_leaf:
            new_node.children = node.children[mid:]
            node.children = node.children[:mid]
            new_node.next = node.next
            node.next = new_node
    
    def _insert_non_full(self, node, key, value):
        if node.is_leaf:
            idx = 0
            while idx < len(node.keys) and node.keys[idx] < key:
                idx += 1
            node.keys.insert(idx, key)
            node.children.insert(idx, value)
        else:
            idx = 0
            while idx < len(node.keys) and node.keys[idx] < key:
                idx += 1
            if len(node.children[idx].keys) == self.order - 1:
                self.split_child(node, idx)
                if key > node.keys[idx]:
                    idx += 1
            self._insert_non_full(node.children[idx], key, value)
    
    def search(self, name):
        key = self.hash_name(name)
        node = self.root
        while not node.is_leaf:
            idx = 0
            while idx < len(node.keys) and key > node.keys[idx]:
                idx += 1
            node = node.children[idx]
        for i, k in enumerate(node.keys):
            if k == key:
                return node.children[i]
        return "Not Found"
    
    def range_search(self, name, greater=True):
        key = self.hash_name(name)
        node = self.root
        while not node.is_leaf:
            idx = 0
            while idx < len(node.keys) and key > node.keys[idx]:
                idx += 1
            node = node.children[idx]
        result = []
        while node:
            for i, k in enumerate(node.keys):
                if (greater and k >= key) or (not greater and k <= key):
                    result.append(node.children[i])
            node = node.next if greater else None
        return result
    
    def delete(self, name):
        key = self.hash_name(name)
        node = self.root
        while not node.is_leaf:
            idx = 0
            while idx < len(node.keys) and key > node.keys[idx]:
                idx += 1
            node = node.children[idx]
        
        for i, k in enumerate(node.keys):
            if k == key:
                del node.keys[i]
                del node.children[i]
                if len(node.keys) < (self.order // 2):
                    self.balance(node)
                if len(node.keys) == 0 and node.next:
                    node.next = node.next.next
                return True
        return "Not Found"
    
    def balance(self, node):
        parent = None
        for p in self._find_parent(self.root, node):
            parent = p
            break

        if not parent:
            return

        idx = parent.children.index(node)
        left_sibling = parent.children[idx - 1] if idx > 0 else None
        right_sibling = parent.children[idx + 1] if idx + 1 < len(parent.children) else None

        if left_sibling and len(left_sibling.keys) > self.order // 2:
            node.keys.insert(0, parent.keys[idx - 1])
            parent.keys[idx - 1] = left_sibling.keys.pop()
            node.children.insert(0, left_sibling.children.pop())
        elif right_sibling and len(right_sibling.keys) > self.order // 2:
            node.keys.append(parent.keys[idx])
            parent.keys[idx] = right_sibling.keys.pop(0)
            node.children.append(right_sibling.children.pop(0))
        else:
            if left_sibling:
                left_sibling.keys.append(parent.keys[idx - 1])
                left_sibling.keys.extend(node.keys)
                left_sibling.children.extend(node.children)
                parent.children.remove(node)
                parent.keys.pop(idx - 1)
            elif right_sibling:
                node.keys.append(parent.keys[idx])
                node.keys.extend(right_sibling.keys)
                node.children.extend(right_sibling.children)
                parent.children.remove(right_sibling)
                parent.keys.pop(idx)
    
    def _find_parent(self, node, target):
        parents = []
        if node.is_leaf:
            return parents
        
        for child in node.children:
            if child == target:
                parents.append(node)
            else:
                parents.extend(self._find_parent(child, target))
        return parents



bpt = BPlusTree()
bpt.insert("Anna", "123-456-7890")
bpt.insert("Artem", "987-654-3210")
bpt.insert("Bohdan", "555-666-7777")

print(bpt.search("Anna"))
print(bpt.range_search("Artem", greater=False))

print(bpt.delete("Bohdan"))
print(bpt.search("Bohdan"))
