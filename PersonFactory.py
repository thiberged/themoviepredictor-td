def insert_people_query(firstname, lastname):
    return (f"INSERT INTO `people` (`firstname`, `lastname`) VALUES ('{firstname}', '{lastname}');")

