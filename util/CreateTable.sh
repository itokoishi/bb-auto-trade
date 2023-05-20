#!/bin/bash

table_name='auto_trade'
table_name_file=${table_name}.json

# 元テーブルのテーブル定義から、create-table用のテーブル定義ファイルを作成する
# AWSから元テーブルのテーブル定義を取得してファイルに出力
aws dynamodb describe-table --table-name ${table_name} > ${table_name_file}

# AWSから出力したテーブル定義を、create-tableに使用できる形に成形してファイルに出力
cat ${table_name_file} |
jq '.Table' |
jq '.TableName = "'${table_name}'"' |
jq 'del(.TableStatus)' |
jq 'del(.CreationDateTime)' |
jq 'del(.ProvisionedThroughput.LastIncreaseDateTime)' |
jq 'del(.ProvisionedThroughput.NumberOfDecreasesToday)' |
jq 'del(.TableSizeBytes)' |
jq 'del(.ItemCount)' |
jq 'del(.TableArn)' |
jq 'del(.TableId)' |
jq 'del(.LatestStreamLabel)' |
jq 'del(.LatestStreamArn)' |
jq 'del(.GlobalSecondaryIndexes[]?.IndexStatus)' |
jq 'del(.GlobalSecondaryIndexes[]?.IndexSizeBytes)' |
jq 'del(.GlobalSecondaryIndexes[]?.ItemCount)' |
jq 'del(.GlobalSecondaryIndexes[]?.IndexArn)' |
jq 'del(.GlobalSecondaryIndexes[]?.ProvisionedThroughput.NumberOfDecreasesToday)' > ${table_name_file}
aws dynamodb create-table --cli-input-json file://${table_name_file} --endpoint-url http://trade-dynamodb-local:8000
