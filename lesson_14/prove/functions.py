"""
Course: CSE 251, week 14
File: functions.py
Author: <Tyler Bartle>

Instructions:

Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04


Requesting a family from the server:
family_id = 6128784944
request = Request_thread(f'{TOP_API_URL}/family/{family_id}')
request.start()
request.join()

Example JSON returned from the server
{
    'id': 6128784944, 
    'husband_id': 2367673859,        # use with the Person API
    'wife_id': 2373686152,           # use with the Person API
    'children': [2380738417, 2185423094, 2192483455]    # use with the Person API
}

Requesting an individual from the server:
person_id = 2373686152
request = Request_thread(f'{TOP_API_URL}/person/{person_id}')
request.start()
request.join()

Example JSON returned from the server
{
    'id': 2373686152, 
    'name': 'Stella', 
    'birth': '9-3-1846', 
    'parent_id': 5428641880,   # use with the Family API
    'family_id': 6128784944    # use with the Family API
}

You will lose 10% if you don't detail your part 1 and part 2 code below

Describe how to speed up part 1

I sped up part 1 by parallelizing the recursive API calls.
Instead of sequentially retrieving each family and person, 
    I spawned threads for each API request.
This allows multiple API calls to run concurrently,
    significantly reducing the overall time.
Proper synchronization (via locks) ensures
    thread-safe updates to shared structures,
    such as the visited sets and the tree.


Describe how to speed up part 2

I sped up the breadth-first search in part 2
    by processing all families in a given generation concurrently.
I spawned threads to retrieve family and person data
    for each family in the current generation,
    and then waited for all threads to complete (by joining)
    before moving on to the next generation.
This level-by-level parallelism maximizes the throughput
    of API calls while maintaining the breadth-first ordering.


Extra (Optional) 10% Bonus to speed up part 3

For the bonus, I used a semaphore to limit
    the number of concurrent API calls to 5.
By wrapping each API request with semaphore acquire and release,
    I controlled the maximum number of active connections.
This approach demonstrates controlled parallelism that
    reduces resource contention on the server,
    while still providing significant speedup.

"""
from common import *
import queue

# -----------------------------------------------------------------------------
def depth_fs_pedigree(family_id, tree, generations):
    """
    Performs a depth-first search to build the pedigree tree using threads for concurrency.
    Uses recursion to fetch family and person data concurrently, speeding up the process.
    """
    
    # Sets to track visited family and person IDs to avoid duplicate processing.
    visited_families = set()
    visited_people = set()
    # Lock to ensure thread-safe updates to shared data structures.
    lock = threading.Lock()

    def process_family(current_family_id, current_generation):
        """
        Recursively processes a family and its associated persons (husband, wife, and children).
        Spawns threads for each API call to retrieve family and person information.
        """
        # Base case: if we've reached the maximum generation, return.
        if current_generation >= generations:
            return
        # Check if the current family has already been processed.
        with lock:
            if current_family_id in visited_families:
                return
            visited_families.add(current_family_id)
        # Retrieve family data from the server.
        family_req = Request_thread(f'{TOP_API_URL}/family/{current_family_id}')
        family_req.start()
        family_req.join()
        family_data = family_req.get_response()
        if not family_data:
            return
        # Create a Family object from the retrieved data and add it to the tree.
        family = Family(family_data)
        tree.add_family(family)
        
        threads = []
        # Process husband concurrently.
        husband_id = family.get_husband()
        if husband_id:
            with lock:
                if husband_id not in visited_people:
                    visited_people.add(husband_id)
                else:
                    husband_id = None
            if husband_id:
                t = threading.Thread(target=process_person, args=(husband_id, current_generation))
                threads.append(t)
                t.start()
        # Process wife concurrently.
        wife_id = family.get_wife()
        if wife_id:
            with lock:
                if wife_id not in visited_people:
                    visited_people.add(wife_id)
                else:
                    wife_id = None
            if wife_id:
                t = threading.Thread(target=process_person, args=(wife_id, current_generation))
                threads.append(t)
                t.start()
        # Process each child concurrently.
        for child_id in family.get_children():
            with lock:
                if child_id not in visited_people:
                    visited_people.add(child_id)
                else:
                    continue
            t = threading.Thread(target=process_person, args=(child_id, current_generation))
            threads.append(t)
            t.start()
        # Wait for all spawned threads to finish.
        for t in threads:
            t.join()

    def process_person(person_id, current_generation):
        """
        Retrieves a person's data from the server, adds them to the tree, and
        determines the next family to process (based on parent or family id).
        """
        # Retrieve person data.
        person_req = Request_thread(f'{TOP_API_URL}/person/{person_id}')
        person_req.start()
        person_req.join()
        person_data = person_req.get_response()
        if not person_data:
            return
        # Create a Person object and add it to the tree.
        person = Person(person_data)
        tree.add_person(person)
        # Determine the next family to process: use parent's id if available, otherwise use family id.
        next_family_id = person.get_parentid() if person.get_parentid() else person.get_familyid()
        if next_family_id:
            process_family(next_family_id, current_generation + 1)

    # Begin the recursive depth-first search from the starting family.
    process_family(family_id, 0)

# -----------------------------------------------------------------------------
def breadth_fs_pedigree(family_id, tree, generations):
    """
    Performs a breadth-first search to build the pedigree tree using threads.
    Processes each generation concurrently.
    """
    visited_families = set()
    visited_people = set()
    lock = threading.Lock()

    def process_family_bfs(fam_id, current_generation, next_level_list):
        """
        Retrieves a family's data, adds it to the tree, and processes associated persons.
        Enqueues the next generation's family IDs into next_level_list.
        """
        # Retrieve family data.
        fam_req = Request_thread(f'{TOP_API_URL}/family/{fam_id}')
        fam_req.start()
        fam_req.join()
        fam_data = fam_req.get_response()
        if not fam_data:
            return
        family = Family(fam_data)
        tree.add_family(family)
        
        def process_and_enqueue(person_id, is_parent=True):
            """
            Retrieves a person's data, adds them to the tree, and enqueues the next family id.
            For parents (husband, wife), uses parent id; for children, uses family id.
            """
            person_req = Request_thread(f'{TOP_API_URL}/person/{person_id}')
            person_req.start()
            person_req.join()
            person_data = person_req.get_response()
            if person_data:
                person = Person(person_data)
                tree.add_person(person)
                # Determine the next family id based on whether this person is a parent or a child.
                next_fam = person.get_parentid() if is_parent else person.get_familyid()
                if next_fam:
                    with lock:
                        if next_fam not in visited_families:
                            next_level_list.append((next_fam, current_generation + 1))
        local_threads = []
        # Process husband and wife concurrently.
        for person_id, _ in [(family.get_husband(), True), (family.get_wife(), True)]:
            if person_id:
                with lock:
                    if person_id not in visited_people:
                        visited_people.add(person_id)
                    else:
                        continue
                t = threading.Thread(target=process_and_enqueue, args=(person_id, True))
                local_threads.append(t)
                t.start()
        # Process each child concurrently.
        for child_id in family.get_children():
            with lock:
                if child_id not in visited_people:
                    visited_people.add(child_id)
                else:
                    continue
            t = threading.Thread(target=process_and_enqueue, args=(child_id, False))
            local_threads.append(t)
            t.start()
        # Wait for all person-processing threads to complete.
        for t in local_threads:
            t.join()
    
    # Initialize BFS with the starting family and generation 0.
    current_level = [(family_id, 0)]
    while current_level:
        next_level = []
        threads = []
        # Process all families in the current generation concurrently.
        for current_family_id, current_generation in current_level:
            if current_generation >= generations:
                continue
            with lock:
                if current_family_id in visited_families:
                    continue
                visited_families.add(current_family_id)
            t = threading.Thread(target=process_family_bfs, args=(current_family_id, current_generation, next_level))
            threads.append(t)
            t.start()
        # Wait for all threads in the current generation to finish.
        for t in threads:
            t.join()
        # Move on to the next generation.
        current_level = next_level

# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(family_id, tree, generations):
    """
    Performs a breadth-first search with a limit of 5 concurrent API calls.
    Uses a semaphore to restrict the number of simultaneous connections to the server.
    """
    visited_families = set()
    visited_people = set()
    lock = threading.Lock()
    # Semaphore to limit the number of concurrent API calls to 5.
    sem = threading.Semaphore(5)

    # Starting list for the BFS: each element is a tuple (family_id, current_generation)
    current_level = [(family_id, 0)]
    while current_level:
        next_level = []
        threads = []

        def process_family_bfs(fam_id, current_generation):
            """
            Retrieves a family's data using the semaphore to limit concurrency.
            Processes associated persons and enqueues next generation family IDs.
            """
            # Acquire semaphore before making the family API call.
            sem.acquire()
            family_req = Request_thread(f'{TOP_API_URL}/family/{fam_id}')
            family_req.start()
            family_req.join()
            # Release semaphore after the API call completes.
            sem.release()

            fam_data = family_req.get_response()
            if not fam_data:
                return

            family = Family(fam_data)
            tree.add_family(family)

            local_threads = []

            def process_person(person_id, is_parent):
                """
                Retrieves a person's data using semaphore control and enqueues the next family ID.
                """
                sem.acquire()
                person_req = Request_thread(f'{TOP_API_URL}/person/{person_id}')
                person_req.start()
                person_req.join()
                sem.release()

                person_data = person_req.get_response()
                if person_data:
                    person = Person(person_data)
                    tree.add_person(person)
                    # Decide which family id to process next based on whether the person is a parent or a child.
                    next_id = person.get_parentid() if is_parent else person.get_familyid()
                    if next_id:
                        with lock:
                            if next_id not in visited_families:
                                next_level.append((next_id, current_generation + 1))
            
            # Process husband concurrently.
            husband_id = family.get_husband()
            if husband_id:
                with lock:
                    if husband_id not in visited_people:
                        visited_people.add(husband_id)
                    else:
                        husband_id = None
                if husband_id:
                    t = threading.Thread(target=process_person, args=(husband_id, True))
                    local_threads.append(t)
                    t.start()
            # Process wife concurrently.
            wife_id = family.get_wife()
            if wife_id:
                with lock:
                    if wife_id not in visited_people:
                        visited_people.add(wife_id)
                    else:
                        wife_id = None
                if wife_id:
                    t = threading.Thread(target=process_person, args=(wife_id, True))
                    local_threads.append(t)
                    t.start()
            # Process each child concurrently.
            for child_id in family.get_children():
                with lock:
                    if child_id in visited_people:
                        continue
                    visited_people.add(child_id)
                t = threading.Thread(target=process_person, args=(child_id, False))
                local_threads.append(t)
                t.start()

            for t in local_threads:
                t.join()

        # Process all families at the current generation concurrently.
        for fam_id, current_generation in current_level:
            if current_generation >= generations:
                continue
            with lock:
                if fam_id in visited_families:
                    continue
                visited_families.add(fam_id)
            t = threading.Thread(target=process_family_bfs, args=(fam_id, current_generation))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # Move to the next generation.
        current_level = next_level