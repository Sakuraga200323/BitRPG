# 目次
 - [BitRPG](#one)
 - [開発者および運営陣紹介](#two)
 - [主要コマンドの解説](#three)
 - [各システムの解説](#four)
# [BitRPG](#one)
ターン制を採用した**RPGBot**です。貴方のサーバーに刺激的な戦いと、ほんの僅かな楽しみを与えます。  
※このBotはデータベースシステムの改良以来ほぼ全てを１から作り直したため、初期に比べて一部の機能が欠落しています（後述）。 
# [開発および運営陣紹介](#two)
#### 初代開発者
* **Amanohashi**#6870
* **Amanohashi**#9999 ※同一人物、故人。
#### 二代目開発者
* **Sakuraga**#2806
#### 運営陣の皆様-ClearanceLevel4
* **箱男**#0101
* **Alpha Null**#5000
# [主要コマンドの解説](#three)
※省略形があるコマンドは"/"で区切ってあります。[ ]があるコマンドは、その中から一つだけ選んで記述してください。[　#] は実際の使用時には不必要です。  
|  コマンド  |  説明  |
| ---- | ---- |
|  **\^\^url**  |  BitRPGに関係するURLの一覧を表示。  |
|  **\^\^status/st**  |  プレイヤーのステータスを表示。  |
|  **\^\^item/i**  |  プレイヤーのインベントリを表示。  |
|  **\^\^item/i [アイテム名]**  |  指定アイテムを使用。  |
|  **^^point [str, def, agi] [強化量]**  |  STPを消費してステータスを強化。  |
|  **\^\^gentotsu**  |  石を消費してレベル上限を解放。  |
# [各システムの解説](#four)
<details>
 <summary>
  <strong>戦闘システム</strong>
 </summary>
  &emsp;BitRPGを導入すると、各チャンネルにモンスターが出現します。全チャンネルに共通で初期1Lvです。一体倒すごとに1Lvずつ上昇していきます。また、特定の条件下で、通常よりも強かったり、経験値量が多いモンスターが出現します。
   &emsp;
 <details>
  <summary>
   各モンスターと性能、効果の違い
  </summary>
	<table>
		<tbody>
			<tr>
				<th></th>
				<th>出現条件</th>
				<th>性能比</th>
				<th>特殊効果</th>
			</tr>
			<tr>
				<td>Elite</td>
				<td>敵のレベルが10の倍数</td>
				<td>ステータスが通常敵の150%</td>
				<td>経験値が通常敵の150%</td>
			</tr>
			<tr>
				<td>Catastrophe</td>
				<td>敵のレベルが100の倍数</td>
				<td>ステータスが通常敵の200%</td>
				<td>経験値が通常敵の500%</td>
			</tr>
			<tr>
				<td>WorldEnd</td>
				<td>敵のレベルが1000の倍数</td>
				<td>通常敵の500%の性能</td>
				<td>験値が通常敵の10000%</td>
			</tr>
			<tr>
				<td>UltraRare</td>
				<td>0.1%をひきあてる</td>
				<td>なし</td>
				<td>経験値が通常敵の10000%</td>
			</tr>		
		</tbody>
	</table>
 </details>
  &emsp;BitRPGではターン制を戦闘システムに採用しています。各ターンには先手後手の概念が存在しています。一般的にはモンスターとプレイヤーのAGIを比較し、優っているほうが先手です。<br>&emsp;攻撃をした時、モンスターとプレイヤーは共に一定の確率で通常よりも高いダメージ値を叩き出します。これはわかりやすくいうとクリティカルの概念です。ダメージの上昇量には<strong>強・超・極</strong>と段階があります。
 &emsp;
 <details>
  <summary>
   各確率とダメージ倍率
  </summary>
	<table>
		<tbody>
			<tr>
				<th></th>
				<th>発動確率</th>
				<th>強化割合</th>
			</tr>
			<tr>
				<td>強ダメージ</td>
				<td>15%</td>
				<td>+50%</td>
			</tr>
			<tr>
				<td>超ダメージ</td>
				<td>10%</td>
				<td>+100%</td>
			</tr>
			<tr>
				<td>極ダメージ</td>
				<td>5%</td>
				<td>+200%</td>
			</tr>
		</tbody>
	</table>
 </details>
</details>
