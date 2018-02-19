docker build -t hw1_sender . 
docker run -it --rm --name producer --network=hw1_default hw1_sender
