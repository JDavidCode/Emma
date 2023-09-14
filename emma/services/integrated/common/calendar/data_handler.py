import sqlite3

def create_event(title, description, start_time, end_time):
    conn = sqlite3.connect('calendar.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO events (title, description, start_time, end_time)
        VALUES (?, ?, ?, ?)
    ''', (title, description, start_time, end_time))

    conn.commit()
    conn.close()

def get_event(event_id):
    conn = sqlite3.connect('calendar.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM events WHERE id = ?', (event_id,))
    event = cursor.fetchone()

    conn.close()

    return event

def get_all_events():
    conn = sqlite3.connect('calendar.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM events')
    events = cursor.fetchall()

    conn.close()

    return events

def update_event(event_id, title, description, start_time, end_time):
    conn = sqlite3.connect('calendar.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE events
        SET title=?, description=?, start_time=?, end_time=?
        WHERE id=?
    ''', (title, description, start_time, end_time, event_id))

    conn.commit()
    conn.close()

def delete_event(event_id):
    conn = sqlite3.connect('calendar.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))

    conn.commit()
    conn.close()
