
                CREATE TABLE auth_user (
                    id INT PRIMARY KEY,
                    username VARCHAR(150),
                    email VARCHAR(254),
                    is_active BOOLEAN
                );
                CREATE TABLE blog_post (
                    id INT PRIMARY KEY,
                    title VARCHAR(200),
                    content TEXT,
                    author_id INT
                );
                