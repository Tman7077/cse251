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

<Add your comments here>


Describe how to speed up part 2

<Add your comments here>


Extra (Optional) 10% Bonus to speed up part 3

<Add your comments here>

"""
from common import *
import queue

# -----------------------------------------------------------------------------
def depth_fs_pedigree(family_id, tree, generations):
    # KEEP this function even if you don't implement it
    # TODO - implement Depth first retrieval
    # TODO - Printing out people and families that are retrieved from the server will help debugging
    
    visited_families = set()
    visited_people = set()
    lock = threading.Lock()

    def process_family(current_family_id, current_generation):
        if current_generation >= generations:
            return
        with lock:
            if current_family_id in visited_families:
                return
            visited_families.add(current_family_id)
        # Retrieve family concurrently
        family_req = Request_thread(f'{TOP_API_URL}/family/{current_family_id}')
        family_req.start()
        family_req.join()
        family_data = family_req.get_response()
        if not family_data:
            return
        family = Family(family_data)
        tree.add_family(family)
        
        threads = []
        # Process husband
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
        # Process wife
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
        # Process children
        for child_id in family.get_children():
            with lock:
                if child_id not in visited_people:
                    visited_people.add(child_id)
                else:
                    continue
            t = threading.Thread(target=process_person, args=(child_id, current_generation))
            threads.append(t)
            t.start()
        # Wait for all spawned threads
        for t in threads:
            t.join()

    def process_person(person_id, current_generation):
        # Retrieve person concurrently
        person_req = Request_thread(f'{TOP_API_URL}/person/{person_id}')
        person_req.start()
        person_req.join()
        person_data = person_req.get_response()
        if not person_data:
            return
        person = Person(person_data)
        tree.add_person(person)
        # Process next generation using parent id (or family id if parent is missing)
        next_family_id = person.get_parentid() if person.get_parentid() else person.get_familyid()
        if next_family_id:
            process_family(next_family_id, current_generation + 1)

    process_family(family_id, 0)

# -----------------------------------------------------------------------------
def breadth_fs_pedigree(family_id, tree, generations):
    # KEEP this function even if you don't implement it
    # TODO - implement breadth first retrieval
    # TODO - Printing out people and families that are retrieved from the server will help debugging

    visited_families = set()
    visited_people = set()
    lock = threading.Lock()

    def process_family_bfs(fam_id, current_generation, next_level_list):
        # Retrieve family data concurrently
        fam_req = Request_thread(f'{TOP_API_URL}/family/{fam_id}')
        fam_req.start()
        fam_req.join()
        fam_data = fam_req.get_response()
        if not fam_data:
            return
        family = Family(fam_data)
        tree.add_family(family)
        # Process husband, wife, and children concurrently
        def process_and_enqueue(person_id, is_parent=True):
            person_req = Request_thread(f'{TOP_API_URL}/person/{person_id}')
            person_req.start()
            person_req.join()
            person_data = person_req.get_response()
            if person_data:
                person = Person(person_data)
                tree.add_person(person)
                # For husband and wife, use parent's id; for children, use family id
                next_fam = person.get_parentid() if is_parent else person.get_familyid()
                if next_fam:
                    with lock:
                        if next_fam not in visited_families:
                            next_level_list.append((next_fam, current_generation + 1))
        local_threads = []
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
        for child_id in family.get_children():
            with lock:
                if child_id not in visited_people:
                    visited_people.add(child_id)
                else:
                    continue
            t = threading.Thread(target=process_and_enqueue, args=(child_id, False))
            local_threads.append(t)
            t.start()
        for t in local_threads:
            t.join()
    
    current_level = [(family_id, 0)]
    while current_level:
        next_level = []
        threads = []
        # Process all families in the current generation concurrently
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
        # Wait for all families in current generation
        for t in threads:
            t.join()
        current_level = next_level

# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(family_id, tree, generations):
    # KEEP this function even if you don't implement it
    # TODO - implement breadth first retrieval
    #      - Limit number of concurrent connections to the FS server to 5
    # TODO - Printing out people and families that are retrieved from the server will help debugging

    visited_families = set()
    visited_people = set()
    lock = threading.Lock()
    # Limit the number of concurrent API calls to 5.
    sem = threading.Semaphore(5)

    # Starting list for the BFS: each element is a tuple (family_id, current_generation)
    current_level = [(family_id, 0)]
    while current_level:
        next_level = []
        threads = []

        def process_family_bfs(fam_id, current_generation):
            # Limit the number of concurrent family requests.
            sem.acquire()
            family_req = Request_thread(f'{TOP_API_URL}/family/{fam_id}')
            family_req.start()
            family_req.join()
            sem.release()

            fam_data = family_req.get_response()
            if not fam_data:
                return

            family = Family(fam_data)
            tree.add_family(family)

            local_threads = []

            # Helper function to process a person (husband, wife, or child)
            def process_person(person_id, is_parent):
                sem.acquire()
                person_req = Request_thread(f'{TOP_API_URL}/person/{person_id}')
                person_req.start()
                person_req.join()
                sem.release()

                person_data = person_req.get_response()
                if person_data:
                    person = Person(person_data)
                    tree.add_person(person)
                    # Decide which family to process next.
                    next_id = person.get_parentid() if is_parent else person.get_familyid()
                    if next_id:
                        with lock:
                            if next_id not in visited_families:
                                next_level.append((next_id, current_generation + 1))

            # Process husband
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

            # Process wife
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

            # Process children
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

        current_level = next_level