# hack to get the docker entrypoint to work ..
cd /code
# while !</dev/tcp/db/5432; do 
#     echo "waiting for database to start"
#     sleep 1; 
# done;
python run_debug_server.py