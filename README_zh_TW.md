# ![WorkbenchIcon](./optics_workbench_icon.svg) Optics Workbench
[ >deutsch< ](README_de.md)
[ >English< ](README.md)

FreeCAD 的幾何光學模組。  
通過你的 FreeCAD 物件進行簡單的光線追蹤。

![screenshot](./examples/example2D.png)
  
## 安裝

### 自動安裝

Optics 工作台可通過 FreeCAD 的 [Addon Manager](https://wiki.freecad.org/AddonManager) 安裝。


### 手動安裝

<details>
<summary>點擊展開顯示手動安裝說明</summary>

```bash
cd ~/.FreeCAD/Mod/ 
git clone https://github.com/chbergmann/OpticsWorkbench.git
```

如果是macOS下，你的FreeCAD Mod路徑可能如下

```
cd ~/Library/Application\ Support/FreeCAD/Mod/
git clone https://github.com/chbergmann/OpticsWorkbench.git
```

如果是Windows路徑可能如下

```
C:\Program Files\FreeCAD X.YY
```

</details>

#### 重要提醒
一旦安裝完成，必須重新啟動 FreeCAD。當重新啟動 FreeCAD 後，"Optics Workbench" 應該會顯示在 [工作台下拉選單](https://freecad.org/wiki/Std_Workbench) 中。
  
## 開始使用
- 創建一些 FreeCAD 設計物件。對於 2D 模擬，草圖就能完成工作。
- 選擇一個或多個設計物件，然後創建光學鏡面，使物件充當鏡子。
- 選擇一個或多個設計物件，然後創建光學吸收體，使物件充當光線的黑牆。
- 選擇一個或多個設計物件，然後創建光學透鏡，使物件充當透鏡。透鏡應該是封閉形狀。
- 在透鏡屬性中選擇一個材料或提供折射率。
- 添加一些光源（光線、光束）。

## 工具
### ![RayIcon](./icons/ray.svg) 光線 (單色)
單一光線進行光線追蹤  
參數:
- 功率：開啟或關閉  
- 球面：False = 光束單向，True = 從中心向所有方向發射的光線
- BeamNrColumns：每列光線的數量
- BeamNrRows：每行光線的數量
- BeamDistance：兩束光線之間的距離
- 隱藏第一部分：隱藏從光源出發到達第一個反射/折射/消失點的光線部分
- 最大光線長度：光線的最大長度
- 最大反射次數：光線的最大反射次數。防止光線進入鏡盒內無限循環。
- 忽略光學元件：光線將忽略的光學物件列表。
- 基礎：如果在此處選擇了一個形狀，將創建一個光學發射器。

### ![SunRayIcon](./icons/raysun.svg) 光線 (陽光)
多條不同波長的可見光光線。  
光線會重疊。如果它們撞擊到透鏡，則會發生色散。請參見 [範例 - 色散](#-example---dispersion) 下方。

### ![2D Beam](./icons/rayarray.svg) 2D 光束
多條光線組成的光束進行光線追蹤  
參數:
* 光線：BeamNrColumns 必須大於 1 才能生成光束

### ![Radial Beam](./icons/sun.svg) 2D 放射性光束
從一點向所有方向發射的光線  
參數:
* 光線：BeamNrColumns 必須大於 1 且 BeamNrRows=1 且 Spherical=True 以生成放射性光束

### ![Spherical Beam](./icons/sun3D.svg) 球面光束
從一點向所有方向發射的光線  
參數:
* 光線：BeamNrColumns 和 BeamNrRows 必須大於 1 且 Spherical=True 才能生成球面光束

### ![Optical Emitter](./icons/emitter.svg) 光學發射器
FreeCAD 物件將作為光學發射器  
選擇一些 FreeCAD 物件、面或邊，然後創建光學發射器
![screenshot](./examples/Emitter.png)  
邊也可以作為基礎選擇：
![screenshot](./examples/example_candle2D.png)

參數與光線工具相同。
具有不同含義的參數：
- 功率：開啟或關閉  
- 球面：（此功能將忽略此參數）
- BeamNrColumns：每列光線在每個選定表面上的分佈數量
- BeamNrRows：每行光線在每個選定表面上的分佈數量
- BeamDistance：（此功能將忽略此參數）
- 基礎：用於光學發射器的基礎形狀。如果選擇固體，則會在每個面上創建光線。你也可以分別選擇面或邊。

### ![Optical Mirror](./icons/mirror.svg) 光學鏡面
FreeCAD 物件將作為鏡子  
* 選擇一些 FreeCAD 物件，然後創建光學鏡面  
請參見 [統計](#Statistics)

### ![Optical Absorber](./icons/absorber.svg) 光學吸收體
FreeCAD 物件將吸收光線  
* 選擇一些 FreeCAD 物件
* 創建光學吸收體  
請參見 [統計](#Statistics)  

### ![Diffraction grating](./icons/grating.svg) 衍射光柵
FreeCAD 物件將進行簡單的一維光柵模擬。  
對簡單的一維光柵進行光線追蹤，依據 [Ludwig 1973](https://doi.org/10.1364/JOSA.63.001105) 進行。

此方法中，光線有額外的屬性順序，當撞擊指定為光學光柵的物件時會被考慮。利用此屬性，可以在單一光柵上模擬多次不同次序的衍射。

光柵根據以下屬性進行定義：  
* 類型：  
	* 反射
	* 透射，且在第一面發生衍射
	* 透射，且在第二面發生衍射
* 線間距
* 線方向，由一組假設的平面定義，這些平面與物體交集並生成光柵線
* 屬性 "順序"  
此外，對於透射光柵，應提供折射率。

衍射光柵的計算方式可以基於光線定義的順序進行，也可以基於撞擊的光柵進行，這樣就能在多個光柵上同時計算不同的衍射順序。  
**注意** 由於此方法模擬光柵的方式，光線數量會迅速增多，尤其是使用陽光等高數量光源時，計算時間也會顯著增加。  
**同時注意**，由於代碼中的漏洞，衍射的模擬可能會有所不準，但在測試中反射和透射光柵的模擬是準確的。

![screenshot](./examples/simple_reflection_grating_set_of_planes.PNG)
*上圖：顯示一個簡單的反射光柵，500 lpm 被陽光照射。平面法線為 010，顯示定義光柵線方向的交集平面集合。*

![screenshot](./examples/simple_transmission_grating.PNG)
*上圖：顯示相同的物體，定義為透射光柵。請注意，衍射發生在第二面，這是光柵類型的規定。*

![screenshot](./examples/echelle_example.PNG)
*上圖：顯示一個簡單的 echelle 分光儀，使用 R2 52.91 lpm 光柵，並對來自順序 -47 到 -82 的陽光進行衍射。每個順序包含大約 5-10 nm，並從藍光到紅光分別採樣。*

請參見 [統計](#Statistics)  

### ![Optical Lens](./icons/lens.svg) 光學透鏡
FreeCAD 物件將作為透鏡  
* 選擇一些 FreeCAD 物件
* 創建光學透鏡  
必須提供折射率。參數「材料」包含一個預定義折射率的列表。  
請參見 [統計](#Statistics)

### ![Off](./icons/Anonymous_Lightbulb_Off.svg) 關閉光源
關閉所有光線和光束

### ![On](./icons/Anonymous_Lightbulb_Lit.svg) (重新)啟動模擬
啟動並重新計算所有光線和光束

## 統計
光學物件有一個參數 `collectStatistics`。如果設為 `true`，則每次開始模擬時會收集一些統計資料：
- `Hits From Ray/Beam...` 這是計數器，顯示有多少光線擊中了此鏡面（只讀）
- `Hit coordinates from ...` 記錄每條光線擊中物體的位置（只讀）。這樣可以在吸收體上以 XY 圖表方式視覺化光線的影像。

### ![plot3D](./icons/scatter3D.svg) 2D/3D 圖表
選擇一個或多個屬性為 `collectStatistics` = true 的光學物件，並顯示光線擊中它們的位置。將會顯示散佈圖，並忽略非吸收物體。若只顯示選定光束源的擊中位置，請將光束的功率設為關閉，以忽略這些光束。切換文件樹中的光束或吸收體的可見性不會影響 3D 散佈圖的顯示。  
如果有三個維度的座標，將顯示 3D 圖表，否則只顯示 2D 圖表。

![screenshot](./examples/plot3Dexample1.png) ![screenshot](./examples/plot3Dexample2.png)
  

### ![CSVexport](./icons/ExportCSV.svg) CSV 光線擊中匯出
創建一個電子表格，列出所有光束擊中所有吸收體的座標。  
前往「試算表工作台」進行進一步數據處理，或將數據匯出為檔案。

![screenshot](./examples/RayHits.png)

### ![Example](./optics_workbench_icon.svg) 範例 - 2D
![screenshot](./examples/example2D.png)

### ![Example](./optics_workbench_icon.svg) 範例 - 3D
![screenshot](./examples/screenshot3D.png)

### ![Example](./optics_workbench_icon.svg) 範例 - 色散
![screenshot](https://pad.ccc-p.org/uploads/upload_210b4dd5466d2837eb76d5e63688a5c1.png)

### ![Example](./optics_workbench_icon.svg) 範例 - 蠟燭
![screenshot](./examples/example_candle.png)

## 問題與疑難排解
請參見 [Github 問題](https://github.com/chbergmann/OpticsWorkbench/issues)

## 討論
請提供反饋或通過 [專用 FreeCAD 討論區](https://forum.freecad.org/viewtopic.php?f=8&t=59860) 與開發者聯繫。

## 授權
GNU 輕量級公共許可證 v3.0 （[授權條款](LICENSE)）