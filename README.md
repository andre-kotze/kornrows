<div align="center">
<p>
   <a align="left" href="https://ultralytics.com/yolov5" target="_blank">
   <img width="850" src="korn.jpg"></a>
</p>
<br>

</div>

## <div align="center">Custom Implementation for Crop Detection</div>

<p>
YOLOv5 is a family of object detection architectures and models pretrained on the COCO dataset, and represents <a href="https://ultralytics.com">Ultralytics</a>
 open-source research into future vision AI methods, incorporating lessons learned and best practices evolved over thousands of hours of research and development.<br>
   This is a customised version for corn plant identification as part of an ongoing research project
</p>


### Training Checkpoints

<p>
kornmodel960m<br>
Locally trained model with 684 images<br>
```--img 960 batch 4 --epochs 100 --data korn.yaml --cfg models/yolov5m.yaml```
<br>
Computing time: ~31 hours<br>
mAP@0.5: unknown
<br><br>
kornmodel960l_1200<br>
Colab trained model with 1200 images<br>
```--img 960 --batch 8 --epochs 150 --data korn.yaml --cfg models/yolov5l.yaml```
<br>
Computing time: ?<br>
mAP@0.5: unknown
<br>
</p>


<br>

