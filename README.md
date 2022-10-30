# Deetect: 
## a deep learning based image analysis tool for quantification of adherent cell populations on oxygenator membranes after extracorporeal membrane oxygenation therapy
an automated deep learning-based all-in-one image processing pipeline for image sequences of the examined ECMO-membranes to quantify cell depositions in certain areas and identify predilection sites for increased cell adherence. 

## Table of Content
- [Experimental dataset](#experimental-dataset)
- [Tools](#tools)
  * [Conventional Segmentation and Counting via FIJI](#conventional-segmentation-and-counting-via-fiji)
  * [Deetect:  deep learning based image analysis tool](#deetect---deep-learning-based-image-analysis-tool)
- [Installation](#installation)
  * [Instructions](#instructions)
- [publications](#publications)
 
 
## Experimental dataset
This dataset is available at: https://edmond.mpdl.mpg.de/dataset.xhtml?persistentId=doi:10.17617/3.2OEMSK  
The experiment was done in four sets, 115 images are generated. The number of images produced in each set is as follows: 
- Set 1 contains 30 imagesequences; 15 from Fiber, 15 from Warp predilection site;   10 from venous (I), 10  from middle (M) and 10 from Arterial (A) part of the oxygenator 
- Set 2 contains 25 imagesequences; 10 from Fiber, 15 from Warp predilection site;   10 from venous (I), 6  from middle (M) and 9 from Arterial (A) part of the oxygenator
- Set 3 contains 30 imagesequences; 15 from Fiber, 15 from Warp predilection site;   10 from venous (I), 10  from middle (M) and 10 from Arterial (A) part of the oxygenator
- Set 4 contains 30 imagesequences; 15 from Fiber, 15 from Warp predilection site;   10 from venous (I), 10  from middle (M) and 10 from Arterial (A) part of the oxygenator


## Tools
### Conventional Segmentation and Counting via FIJI 
In this approach a macro was programmed in FIJI to automatically quantify the cell count. It was written in Image-J macro script language. In the first two steps, the images were automatically thresholded using the Li-white method [13]. It was used to set a threshold for the intensity and remove background noise and artifacts from the image to emphasise the cell nucleus structures. Since areas of increased nucleus density lose their differentiability using a threshold the watershed tool was used in the next step. In this morphological process a topographic map of the image is virtually flooded and wherev-er two watersheds meet, the method assumes two contiguous cell cores and draws a di-viding line between the touching objects. The final step of the macro was the counting of the cell nuclei via the analyze-particles function. It scans the image until it detects the edge of an object. It outlines the object boundaries and measures the area. The steps are repeated until the entire image is scanned. 
The minimum size of the objects to be counted was set to 20 pixels2. The roundness (cir-cularity) of the objects to be detected was set to was set to 0 - 1 due to the different shapes of the cell nuclei. After execution of the function, the result is displayed as an overview drawing with a representation of the object outlines and a result table. 
You can find the FIJI macro [here](https://github.com/zgormez/Deetect/blob/main/DAPI%20Counting.ijm)
![Makro workflow](https://user-images.githubusercontent.com/107420190/191925245-eebd4790-2f81-4d38-ad59-e1392bf858a4.png)


### Deetect:  deep learning based image analysis tool

Especially in highly aggregated areas of the investigated samples, only a low dif-ferentiation of individual cell nuclei could be expected using the conventional semantic segmentation applied in FIJI. An AI-based method was developed to better resolve these areas, as it was expected to perform better than conventional segmentation [14]. Never-theless, a central problem in applying these methods is that they involve many sub-processes (pre-, main-, post-processing) that are difficult to modulate by scientists that are inexperienced in programming.
To solve this gap, an automated, compact, deep learning-based ready-to-use image processing tool (ConfoQuant) was developed for the quantification process. It has a graphical user interface (GUI) and many different features to handle problems that oc-curred during the quantification process. 
![Deetect workflow](https://github.com/zgormez/Deetect/blob/main/images/Deetect_workflow_09.22.png)

## Installation
### Instructions
1. Install an [Anaconda](https://www.anaconda.com/download/) distribution of Python -- Choose **Python 3.8** and your operating system.
2. Download Deetect [Deetect file](Deetect)
3. Open an anaconda prompt and create a new environment with `conda env create --file deetect_env.yml`.
4. Activate the environment, run `conda activate deetect`
5. Go to Deetect directory and run 'python main_window.py' 
--------------------
## publications
* The study is based on findings and data from a doctoral thesis by Felix Hoeren.
* This study was presented at the GCB 2021, Germany. You can find the submitted abstract [here](https://github.com/zgormez/Deetect/blob/main/papers/GCB_2021_G%C3%B6rmez_Hoeren_Richter_Krause_Troidl.pdf).
