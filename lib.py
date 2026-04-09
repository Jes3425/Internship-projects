import sqlite3
from datetime import datetime

class LibraryManagement:
    def __init__(self, db_name="library.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.init_db()

    def init_db(self):
        """Initialize database connection and create tables"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        
        # Create 1
        # books table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    isbn TEXT UNIQUE,
                    status TEXT DEFAULT 'available',
                    issued_to TEXT,
                    issue_date TEXT
                )''')
        
        self.conn.commit()

    def add_book(self, title, author, isbn):
        """Add a new book to the library"""
        try:
            title = title.strip() if isinstance(title, str) else title
            author = author.strip() if isinstance(author, str) else author
            isbn = isbn.strip() if isinstance(isbn, str) else isbn
            
            if not title or not author or not isbn:
                print("✗ Error: Title, author, and ISBN cannot be empty!")
                return False
            
            self.cursor.execute("INSERT INTO books (title, author, isbn, status) VALUES (?, ?, ?, ?)",
                              (title, author, isbn, 'available'))
            self.conn.commit()
            print(f"✓ Book '{title}' added successfully!")
            return True
        except sqlite3.IntegrityError:
            print("✗ Error: ISBN already exists!")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def view_all_books(self):
        """Display all books in the library"""
        try:
            self.cursor.execute('SELECT id, title, author, isbn, status, issued_to FROM books')
            books = self.cursor.fetchall()
            
            if not books:
                print("No books in the library.")
                return
            
            print("\n" + "="*100)
            print(f"{'ID':<5} {'Title':<25} {'Author':<20} {'ISBN':<15} {'Status':<12} {'Issued To':<20}")
            print("="*100)
            for book in books:
                print(f"{book[0]:<5} {book[1]:<25} {book[2]:<20} {book[3]:<15} {book[4]:<12} {book[5] or 'N/A':<20}")
            print("="*100)
        except Exception as e:
            print(f"✗ Error: {e}")

    def search_book(self, query, search_type="title"):
        """Search for books by title or author"""
        try:
            query = query.strip() if isinstance(query, str) else query
            if not query:
                print("✗ Error: Search query cannot be empty!")
                return
            
            if search_type.lower() == "title":
                self.cursor.execute('SELECT id, title, author, isbn, status, issued_to FROM books WHERE title LIKE ?',
                                  (f"%{query}%",))
            elif search_type.lower() == "author":
                self.cursor.execute('SELECT id, title, author, isbn, status, issued_to FROM books WHERE author LIKE ?',
                                  (f"%{query}%",))
            else:
                print("Invalid search type. Use 'title' or 'author'.")
                return
            
            results = self.cursor.fetchall()
            
            if not results:
                print(f"No books found with {search_type} containing '{query}'.")
                return
            
            print("\n" + "="*100)
            print(f"Search results for {search_type}: '{query}'")
            print("="*100)
            print(f"{'ID':<5} {'Title':<25} {'Author':<20} {'ISBN':<15} {'Status':<12} {'Issued To':<20}")
            print("="*100)
            for book in results:
                print(f"{book[0]:<5} {book[1]:<25} {book[2]:<20} {book[3]:<15} {book[4]:<12} {book[5] or 'N/A':<20}")
            print("="*100)
        except Exception as e:
            print(f"✗ Error: {e}")

    def issue_book(self, book_id, issued_to):
        """Issue a book to a user"""
        try:
            if not isinstance(book_id, int):
                print("✗ Error: Invalid book ID!")
                return False
            
            issued_to = issued_to.strip() if isinstance(issued_to, str) else issued_to
            if not issued_to:
                print("✗ Error: Person name cannot be empty!")
                return False
            
            self.cursor.execute('SELECT id, title, status FROM books WHERE id = ?', (book_id,))
            book = self.cursor.fetchone()
            
            if not book:
                print("✗ Book not found!")
                return False
            
            if book[2] == 'issued':
                print(f"✗ Book '{book[1]}' is already issued!")
                return False
            
            issue_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('UPDATE books SET status = ?, issued_to = ?, issue_date = ? WHERE id = ?',
                              ('issued', issued_to, issue_date, book_id))
            self.conn.commit()
            print(f"✓ Book '{book[1]}' issued to {issued_to} on {issue_date}!")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def return_book(self, book_id):
        """Return an issued book"""
        try:
            if not isinstance(book_id, int):
                print("✗ Error: Invalid book ID!")
                return False
            
            self.cursor.execute('SELECT id, title, status FROM books WHERE id = ?', (book_id,))
            book = self.cursor.fetchone()
            
            if not book:
                print("✗ Book not found!")
                return False
            
            if book[2] == 'available':
                print(f"✗ Book '{book[1]}' is already available!")
                return False
            
            self.cursor.execute('UPDATE books SET status = ?, issued_to = NULL, issue_date = NULL WHERE id = ?',
                              ('available', book_id))
            self.conn.commit()
            print(f"✓ Book '{book[1]}' returned successfully!")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def delete_book(self, book_id):
        """Delete a book from the library"""
        try:
            if not isinstance(book_id, int):
                print("✗ Error: Invalid book ID!")
                return False
            
            self.cursor.execute('SELECT id, title, status FROM books WHERE id = ?', (book_id,))
            book = self.cursor.fetchone()
            
            if not book:
                print("✗ Book not found!")
                return False
            
            if book[2] == 'issued':
                print(f"✗ Cannot delete issued book '{book[1]}'!")
                return False
            
            self.cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
            self.conn.commit()
            print(f"✓ Book '{book[1]}' deleted successfully!")
            return True
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def view_issued_books(self):
        """Display all currently issued books"""
        try:
            self.cursor.execute('SELECT id, title, author, issued_to, issue_date FROM books WHERE status = ?', ('issued',))
            books = self.cursor.fetchall()
            
            if not books:
                print("No books are currently issued.")
                return
            
            print("\n" + "="*80)
            print(f"{'ID':<5} {'Title':<25} {'Author':<20} {'Issued To':<15} {'Issue Date':<15}")
            print("="*80)
            for book in books:
                print(f"{book[0]:<5} {book[1]:<25} {book[2]:<20} {book[3]:<15} {book[4]:<15}")
            print("="*80)
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def get_valid_input(prompt, input_type=str):
    """Get and validate user input"""
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input:
                print("✗ Input cannot be empty!")
                continue
            if input_type == int:
                return int(user_input)
            return user_input
        except ValueError:
            print(f"✗ Invalid input! Please enter a valid {input_type.__name__}.")

def display_menu():
    """Display the main menu"""
    print("\n" + "="*50)
    print("      LIBRARY MANAGEMENT SYSTEM")
    print("="*50)
    print("1. Add a new book")
    print("2. View all books")
    print("3. Search book by title")
    print("4. Search book by author")
    print("5. Issue a book")
    print("6. Return a book")
    print("7. Delete a book")
    print("8. View issued books")
    print("9. Exit")
    print("="*50)

def main():
    """Main application loop"""
    lib = LibraryManagement()
    
    try:
        while True:
            display_menu()
            choice = input("Enter your choice (1-9): ").strip()
            
            if choice == '1':
                title = get_valid_input("Enter book title: ")
                author = get_valid_input("Enter author name: ")
                isbn = get_valid_input("Enter ISBN: ")
                lib.add_book(title, author, isbn)
            
            elif choice == '2':
                lib.view_all_books()
            
            elif choice == '3':
                query = get_valid_input("Enter book title to search: ")
                lib.search_book(query, "title")
            
            elif choice == '4':
                query = get_valid_input("Enter author name to search: ")
                lib.search_book(query, "author")
            
            elif choice == '5':
                lib.view_all_books()
                book_id = get_valid_input("Enter book ID to issue: ", int)
                issued_to = get_valid_input("Enter name of person issuing the book: ")
                lib.issue_book(book_id, issued_to)
            
            elif choice == '6':
                lib.view_issued_books()
                book_id = get_valid_input("Enter book ID to return: ", int)
                lib.return_book(book_id)
            
            elif choice == '7':
                lib.view_all_books()
                book_id = get_valid_input("Enter book ID to delete: ", int)
                lib.delete_book(book_id)
            
            elif choice == '8':
                lib.view_issued_books()
            
            elif choice == '9':
                print("Thank you for using Library Management System!")
                break
            
            else:
                print("✗ Invalid choice! Please select a valid option (1-9).")
    
    except KeyboardInterrupt:
        print("\n\nApplication terminated by user.")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    finally:
        lib.close()

if __name__ == "__main__":
    main()