import boto3

def lambda_handler(event, context):
    # EC2クライアントの初期化（東京リージョン 'ap-northeast-1'）
    ec2 = boto3.client('ec2', region_name='ap-northeast-1')
    
    # タグ「AutoStop = true」が付いていて、かつ「実行中(running)」のEC2を取得
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:AutoStop',
                'Values': ['true']
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]
    )
    
    # 該当するインスタンスIDを抽出
    instance_ids = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])
            
    # 該当するインスタンスがあれば停止処理を実行
    if instance_ids:
        print(f"停止対象のEC2が見つかりました: {instance_ids}")
        ec2.stop_instances(InstanceIds=instance_ids)
        return f"以下のEC2を停止しました: {instance_ids}"
    else:
        print("停止対象（running状態かつAutoStop=true）のEC2はありません。")
        return "停止対象のEC2はありませんでした。"
