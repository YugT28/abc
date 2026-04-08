import time
from datetime import datetime
from collections import deque

class ManagedObj:
    """
    A class that fully manages its own instances using class-level variables and methods.
    """
    
    # --- Class Variables (Shared globally across all objects) ---
    max_concurrent = 10
    pending_queue = deque()
    active_list = []
    start_time = None

    def __init__(self, obj_id):
        self.status = "Active"
        self.id = obj_id
        
        # When an object is created, it automatically registers ITSELF to the class queue!
        self.__class__.pending_queue.append(self)

    # --- Class Methods (Act on the Class state, not the instance state) ---
    
    @classmethod
    def _replenish_active_list(cls):
        """Pulls from pending_queue to ensure active_list is at max capacity."""
        spaces_available = cls.max_concurrent - len(cls.active_list)
        
        while spaces_available > 0 and cls.pending_queue:
            next_obj = cls.pending_queue.popleft()
            cls.active_list.append(next_obj)
            spaces_available -= 1

    @classmethod
    def start_processing(cls):
        """Starts the main event loop to process active objects."""
        cls.start_time = datetime.now()
        cls._replenish_active_list()
        
        print(f"Starting Process! Initial Active IDs: {[i.id for i in cls.active_list]}")

        while cls.active_list:
            current_time = datetime.now()
            time_elapsed = (current_time - cls.start_time).seconds
            
            items_removed = False

            # We iterate over a slice [:] so we can safely remove from the original list
            for obj in cls.active_list[:]:
                # Simulated Job Completion condition
                if time_elapsed >= (obj.id * 2):
                    cls.active_list.remove(obj)
                    items_removed = True
            
            # If items finished, replenish our active pool
            if items_removed:
                cls._replenish_active_list()
                print(f"Queue updated -> Active IDs: {[i.id for i in cls.active_list]}")
            
            # Small sleep to prevent 100% CPU lock up in the while loop
            time.sleep(0.5)
            
        print("All jobs completed perfectly!")

if __name__ == "__main__":
    initial_ids = list(range(1, 19))
    
    # 1. We just "spawn" the objects. We don't even need to assign them to variables
    # because __init__ automatically registers them to the Class Queue!
    for i in initial_ids:
        ManagedObj(i)
        
    print(f"Number of items in pending queue: {len(ManagedObj.pending_queue)}")
    
    # 2. Run the process directly from the Class! No instance necessary.
    ManagedObj.start_processing()
