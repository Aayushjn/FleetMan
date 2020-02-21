# Start Ditto
#docker-compose -f ~/Desktop/College/4th\ Year/Major\ Project/ditto/deployment/docker/docker-compose.yml up -d

# Create policy
http -a fleetman-dev:fleetman PUT http://localhost:8080/api/2/policies/com.fleetman:policy < ~/IdeaProjects/FleetMan/ditto/policy/policy.json

# Create twins
http -a fleetman-dev:fleetman PUT http://localhost:8080/api/2/things/com.fleetman:12345678912345678 < ~/IdeaProjects/FleetMan/ditto/thing/twin_1.json
http -a fleetman-dev:fleetman PUT http://localhost:8080/api/2/things/com.fleetman:12344862397345673 < ~/IdeaProjects/FleetMan/ditto/thing/twin_2.json
http -a fleetman-dev:fleetman PUT http://localhost:8080/api/2/things/com.fleetman:41654199297345675 < ~/IdeaProjects/FleetMan/ditto/thing/twin_3.json
http -a fleetman-dev:fleetman PUT http://localhost:8080/api/2/things/com.fleetman:41654199297345679 < ~/IdeaProjects/FleetMan/ditto/thing/twin_4.json
http -a fleetman-dev:fleetman PUT http://localhost:8080/api/2/things/com.fleetman:98716931387431697 < ~/IdeaProjects/FleetMan/ditto/thing/twin_5.json
http -a fleetman-dev:fleetman PUT http://localhost:8080/api/2/things/com.fleetman:32164894198433952 < ~/IdeaProjects/FleetMan/ditto/thing/twin_6.json
http -a fleetman-dev:fleetman PUT http://localhost:8080/api/2/things/com.fleetman:87465413196846116 < ~/IdeaProjects/FleetMan/ditto/thing/twin_7.json
http -a fleetman-dev:fleetman PUT http://localhost:8080/api/2/things/com.fleetman:74149874641316844 < ~/IdeaProjects/FleetMan/ditto/thing/twin_8.json
http -a fleetman-dev:fleetman PUT http://localhost:8080/api/2/things/com.fleetman:74134941132143712 < ~/IdeaProjects/FleetMan/ditto/thing/twin_9.json
http -a fleetman-dev:fleetman PUT http://localhost:8080/api/2/things/com.fleetman:54327932973250721 < ~/IdeaProjects/FleetMan/ditto/thing/twin_10.json
