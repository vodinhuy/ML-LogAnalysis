import svr

logserver = svr.LogServer("./server/config.json")

if __name__ == "__main__":
    logserver.run_loop()
