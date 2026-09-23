# 【AWS / Python】AWS LambdaとEventBridgeによるEC2自動コスト削減仕組みの構築

## 1. 概要・開発の背景
学習・検証用に作成したAWS EC2インスタンスの消し忘れ（課金発生）を防ぐため、特定のタグが付いたEC2インスタンスを自動で停止する仕組みを構築しました。

「インフラ運用の自動化」と「クラウドコストの最適化」を実戦形式で学ぶことを目的としています。

---

## 2. システム構成図
【ここにDraw.ioやCloudcraftなどで作成した構成図の画像】
┌─────────────────────────────────────────────────────────┐
│ [AWS Cloud]                                             │
│                                                         │
│  ┌──────────────┐      ┌──────────────┐      ┌────────┐ │
│  │ EventBridge  │ ───> │  AWS Lambda  │ ───> │  EC2   │ │
│  └──────────────┘      └──────────────┘      └────────┘ │
│   (Cron: 19:00)         (Python Script)     (AutoStop)  │
│                               │                         │
│                               ▼                         │
│                        ┌──────────────┐                 │
│                        │   IAM Role   │                 │
│                        └──────────────┘                 │
└─────────────────────────────────────────────────────────┘

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

QiitaやGitHub（README.md）、noteにそのまま貼り付けて使える「アウトプット用テンプレート」を作成しました。

エンジニアの採用担当者（面接官）は、**「なぜ作ったか（目的）」「どんな技術を使ったか（構成）」「課題をどう解決したか（問題解決能力）」** の3点を重視して見ています。

以下のテンプレートの `【 】` 部分を自分の言葉に書き換えて発信してみてください。

---

### Qiita / GitHub README 用テンプレート

以下の枠内をコピーし、Markdown形式で書き換えて利用できます。

```markdown
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

```

---

## 5. 工夫した点・ハマったところと解決策

### ① 最小権限を意識したIAMロールの設定

Lambdaに無制限の権限を与えるのではなく、EC2の操作に必要な最小限の権限（`AmazonEC2FullAccess` 等）を設定し、クラウドのセキュリティ原則（最小権限の付与）を学びました。

### ② タイムアウトエラー（Task timed out）の解決

**【課題】**

初回実行時、`Task timed out after 3.00 seconds` というエラーが発生し、処理が失敗しました。

**【原因】**

Lambdaのデフォルトタイムアウト制限が「3秒」と短く、boto3経由でのEC2 API呼び出し・レスポンス待ちの間に制限時間を迎えてしまっていました。

**【解決策】**

Lambdaの一般設定からタイムアウト時間を `15秒` に拡張することで、正常に処理が最後まで完了するよう改善しました。

---

## 6. まとめ・今後の展望

今回の構築を通して、サーバーレス（Lambda）を活用した運用の自動化や、エラーログ（CloudWatch Logs / テスト結果）からのデバッグ手法を学ぶことができました。



```

---


```
