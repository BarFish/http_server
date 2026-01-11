# **http://127.0.0.1:8080/** - 200 OK - shows home page.
![alt text](evidence/200.png)

# **http://127.0.0.1:8080/bar** - 404 Not Found
![alt text](evidence/404.png)

# **http://127.0.0.1:8080/secret.html** - 403 Forbidden
![alt text](evidence/403.png)

# **http://127.0.0.1:8080/page1.html** - 302 Redirection then 200 OK - shows home page.
![alt text](evidence/302.png)

# Costum check (rased error) 500 Internal
![alt text](evidence/500.png)

# 4_5/6 Calc Next - **http://127.0.0.1:8080/calculate-next?num=-100** - 200 OK
![alt text](evidence/calc_next.png)

# 4_9 Calc Area - **http://127.0.0.1:8080/calculate-area?height=10&width=6** - 200 OK
![alt text](evidence/calc_area.png)

# 4_10 Upload Image - **http://127.0.0.1:8080/upload?file-name=test-image.jpg** - 200 OK
![alt text](evidence/4_10.png)

# 4_11 Show Image - **http://127.0.0.1:8080/image?image-name=test-image.jpg** - 200 OK
![alt text](evidence/4_11.png)