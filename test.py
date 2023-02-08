 # Add the following code to send a random file in a random time between 0 and 30 seconds
        time.sleep(random.uniform(0, 30))  # sleep for a random time between 0 and 30 seconds
        filename = random.choice(os.listdir())  # select a random file from the current directory
        signal = "send file"
        with open(filename, 'rb') as f:
            client_connection.send(signal.encode())
            recu = client_connection.recv(1024)
            if recu.decode() == "GO" :
                client_connection.sendfile(f)  # send the file to the client
        print(f"Sent random file {filename} to client {client_connection.getpeername()}")