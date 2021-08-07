"""
Traditional tree walks:
- Pre-order walk
- Post-order walk [not implemented yet]
- In-order walk - for binary trees [not implemented yet]
"""



if __name__ == '__main__':
    from PaladinEngine.tests.test_resources.lab1.lib.adt.tree.build import TreeAssistant
    
    inputs = [(1, [(2, [3, 4, 5]), (6, [(7, [8]), 9])])]
    
    for input in inputs: #@ReservedAssignment
        tree = TreeAssistant.build(input)
        print(tree)
        print([x.root for x in PreorderWalk(tree)])
