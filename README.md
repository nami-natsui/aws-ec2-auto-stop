# 【AWS / Python】AWS LambdaとEventBridgeによるEC2自動コスト削減仕組みの構築

## 1. 概要・開発の背景
学習・検証用に作成したAWS EC2インスタンスの消し忘れ（課金発生）を防ぐため、特定のタグが付いたEC2インスタンスを自動で停止する仕組みを構築しました。

「インフラ運用の自動化」と「クラウドコストの最適化」を実戦形式で学ぶことを目的としています。

---

## 2. システム構成図
ここにDraw.ioやCloudcraftなどで作成した構成図の画像を貼り付けます。

【処理の流れ】
1. Amazon EventBridge（タイマー）が指定時刻にLambdaを起動
2. AWS Lambda（Python）がEC2の情報を取得
3. タグ `AutoStop = true` かつ `running` 状態のEC2を検出
4. 対象のEC2に対して停止処理（stop_instances）を実行

---

## 3. 使用技術・開発環境
- **Cloud:** AWS (EC2, Lambda, EventBridge, IAM)
- **Language:** Python 3.12 (boto3)
- **Tool:** AWS Management Console

---

## 4. 実装コード (Python / boto3)

```python
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2', region_name='ap-northeast-1')
    
    # タグ「AutoStop = true」が付いていて「running」状態のEC2を取得
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:AutoStop', 'Values': ['true']},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    
    instance_ids = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])
            
    if instance_ids:
        print(f"停止対象のEC2が見つかりました: {instance_ids}")
        ec2.stop_instances(InstanceIds=instance_ids)
        return f"以下のEC2を停止しました: {instance_ids}"
    else:
        print("停止対象のEC2はありません。")
        return "停止対象のEC2はありませんでした。"
