disk_usage=$(df -h / | grep '/' | tr -s ' ' | cut -d' ' -f5 | tr -d '%')
json_output=$(jq -n --argjson usage "$disk_usage" '{disk_usage: $usage}') # crée objet en json
echo $json_output
