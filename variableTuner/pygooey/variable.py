
class Variable:

    def __init__(self, name, displayFormat, min, max, increment):
        """ name: The  variable name 
            displayFormat: for instance %.4f or %d
        """
        
        
                
                
        self.name = name
        self.displayFormat = displayFormat
        self.min = min
        self.max = max
        self.increment = increment

    