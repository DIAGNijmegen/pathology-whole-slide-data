diff --git a/notebooks/04 - WholeSlideConfiguration.ipynb b/notebooks/04 - WholeSlideConfiguration.ipynb
index 95c902b..2909c81 100644
--- a/notebooks/04 - WholeSlideConfiguration.ipynb	
+++ b/notebooks/04 - WholeSlideConfiguration.ipynb	
@@ -34,22 +34,7 @@
    "cell_type": "code",
    "execution_count": 3,
    "metadata": {},
-   "outputs": [
-    {
-     "ename": "FileNotFoundError",
-     "evalue": "config not found: /home/mart/anaconda3/envs/wholeslidedata/lib/python3.8/site-packages/wholeslidedata/configuration/config_files/config.yml",
-     "output_type": "error",
-     "traceback": [
-      "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
-      "\u001b[0;31mFileNotFoundError\u001b[0m                         Traceback (most recent call last)",
-      "\u001b[0;32m<ipython-input-3-373c1cb46f6d>\u001b[0m in \u001b[0;36m<module>\u001b[0;34m\u001b[0m\n\u001b[0;32m----> 1\u001b[0;31m \u001b[0mbuild\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mWholeSlideDataConfiguration\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mbuild\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0muser_config\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0mUSER_CONFIG\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mmodes\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0mMODES\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m      2\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      3\u001b[0m \u001b[0mtraining_dataset\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mbuild\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'wholeslidedata'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'training'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'dataset'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      4\u001b[0m \u001b[0mtraining_batch_sampler\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mbuild\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'wholeslidedata'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'training'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'batch_sampler'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m      5\u001b[0m \u001b[0mtraining_batch_shape\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mbuild\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'wholeslidedata'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'training'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'batch_shape'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
-      "\u001b[0;32m~/anaconda3/envs/wholeslidedata/lib/python3.8/site-packages/creationism/configuration/config.py\u001b[0m in \u001b[0;36mbuild\u001b[0;34m(cls, user_config, modes, build_instances, build_key, presets, external_configurations, search_paths, *args, **kwargs)\u001b[0m\n\u001b[1;32m    281\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    282\u001b[0m         \u001b[0minclude_configs\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0muser_config\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0msearch_paths\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0msearch_paths\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m--> 283\u001b[0;31m         \u001b[0mconfiguration\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mcls\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0;34m*\u001b[0m\u001b[0margs\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0;34m**\u001b[0m\u001b[0mkwargs\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m    284\u001b[0m         \u001b[0;32mfor\u001b[0m \u001b[0mpreset\u001b[0m \u001b[0;32min\u001b[0m \u001b[0mpresets\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m    285\u001b[0m             preset_config = open_config(\n",
-      "\u001b[0;32m~/anaconda3/envs/wholeslidedata/lib/python3.8/site-packages/wholeslidedata/configuration/config.py\u001b[0m in \u001b[0;36m__init__\u001b[0;34m(self, modes, search_paths)\u001b[0m\n\u001b[1;32m     19\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     20\u001b[0m         \u001b[0msearch_paths_\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0m__class__\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mSEARCH_PATHS\u001b[0m \u001b[0;34m+\u001b[0m \u001b[0msearch_paths\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m---> 21\u001b[0;31m         config_value = open_config(\n\u001b[0m\u001b[1;32m     22\u001b[0m             \u001b[0mWholeSlideDataConfiguration\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mCONFIG_PATH\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0msearch_paths\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0msearch_paths_\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     23\u001b[0m         )\n",
-      "\u001b[0;32m~/anaconda3/envs/wholeslidedata/lib/python3.8/site-packages/creationism/configuration/extensions.py\u001b[0m in \u001b[0;36mopen_config\u001b[0;34m(config_path, search_paths)\u001b[0m\n\u001b[1;32m     47\u001b[0m             \u001b[0;32mpass\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     48\u001b[0m     \u001b[0;32melse\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m---> 49\u001b[0;31m         \u001b[0;32mraise\u001b[0m \u001b[0mFileNotFoundError\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0;34mf\"config not found: {config_path}\"\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m",
-      "\u001b[0;31mFileNotFoundError\u001b[0m: config not found: /home/mart/anaconda3/envs/wholeslidedata/lib/python3.8/site-packages/wholeslidedata/configuration/config_files/config.yml"
-     ]
-    }
-   ],
+   "outputs": [],
    "source": [
     "build = WholeSlideDataConfiguration.build(user_config=USER_CONFIG, modes=MODES)\n",
     "\n",
@@ -63,12 +48,48 @@
   },
   {
    "cell_type": "code",
-   "execution_count": 140,
+   "execution_count": 9,
    "metadata": {},
-   "outputs": [],
+   "outputs": [
+    {
+     "data": {
+      "text/plain": [
+       "[WholeSlideSampleReference(file_index=0, file_key='TCGA-21-5784-01Z-00-DX1', wsa_index=0, annotation_index=0),\n",
+       " WholeSlideSampleReference(file_index=0, file_key='TCGA-21-5784-01Z-00-DX1', wsa_index=0, annotation_index=1)]"
+      ]
+     },
+     "execution_count": 9,
+     "metadata": {},
+     "output_type": "execute_result"
+    }
+   ],
+   "source": [
+    "[training_dataset.sample_references['lymphocytes'][0],\n",
+    "                                               training_dataset.sample_references['lymphocytes'][1]]"
+   ]
+  },
+  {
+   "cell_type": "code",
+   "execution_count": 10,
+   "metadata": {},
+   "outputs": [
+    {
+     "ename": "KeyError",
+     "evalue": "'point'",
+     "output_type": "error",
+     "traceback": [
+      "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
+      "\u001b[0;31mKeyError\u001b[0m                                  Traceback (most recent call last)",
+      "\u001b[0;32m<ipython-input-10-d0e5fb35428a>\u001b[0m in \u001b[0;36m<module>\u001b[0;34m\u001b[0m\n\u001b[0;32m----> 1\u001b[0;31m training_batch = training_batch_sampler.batch([{'reference': training_dataset.sample_references['lymphocytes'][0]},\n\u001b[0m\u001b[1;32m      2\u001b[0m                                                {'reference': training_dataset.sample_references['lymphocytes'][1]}])\n\u001b[1;32m      3\u001b[0m \u001b[0mx_batch\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0my_batch\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mtraining_batch\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
+      "\u001b[0;32m~/Radboudumc/code/libs/pathology-whole-slide-data/wholeslidedata/samplers/batchsampler.py\u001b[0m in \u001b[0;36mbatch\u001b[0;34m(self, batch_data, i)\u001b[0m\n\u001b[1;32m     15\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     16\u001b[0m     \u001b[0;32mdef\u001b[0m \u001b[0mbatch\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mself\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mbatch_data\u001b[0m\u001b[0;34m:\u001b[0m \u001b[0mList\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0mWholeSlideSampleReference\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mi\u001b[0m\u001b[0;34m=\u001b[0m\u001b[0;32mNone\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m:\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m---> 17\u001b[0;31m         \u001b[0mbatch_data\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0m_sample_batch\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mbatch_data\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mi\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m     18\u001b[0m         \u001b[0mbatch_data\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0m_apply_batch_callbacks\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mbatch_data\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     19\u001b[0m         \u001b[0;32mreturn\u001b[0m \u001b[0mbatch_data\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n",
+      "\u001b[0;32m~/Radboudumc/code/libs/pathology-whole-slide-data/wholeslidedata/samplers/batchsampler.py\u001b[0m in \u001b[0;36m_sample_batch\u001b[0;34m(self, batch_data, i)\u001b[0m\n\u001b[1;32m     26\u001b[0m             \u001b[0mwsi\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0m_dataset\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mget_image_from_reference\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0msample_reference\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'reference'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     27\u001b[0m             \u001b[0mwsa\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0m_dataset\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0mget_wsa_from_reference\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0msample_reference\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'reference'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0;32m---> 28\u001b[0;31m             \u001b[0mpoint\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0msample_reference\u001b[0m\u001b[0;34m[\u001b[0m\u001b[0;34m'point'\u001b[0m\u001b[0;34m]\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[0m\u001b[1;32m     29\u001b[0m             \u001b[0mx_samples\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0my_samples\u001b[0m \u001b[0;34m=\u001b[0m \u001b[0mself\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0m_sampler\u001b[0m\u001b[0;34m.\u001b[0m\u001b[0msample\u001b[0m\u001b[0;34m(\u001b[0m\u001b[0mwsi\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mwsa\u001b[0m\u001b[0;34m,\u001b[0m \u001b[0mpoint\u001b[0m\u001b[0;34m)\u001b[0m\u001b[0;34m\u001b[0m\u001b[0;34m\u001b[0m\u001b[0m\n\u001b[1;32m     30\u001b[0m \u001b[0;34m\u001b[0m\u001b[0m\n",
+      "\u001b[0;31mKeyError\u001b[0m: 'point'"
+     ]
+    }
+   ],
    "source": [
-    "training_batch = training_batch_sampler.batch([training_dataset.sample_references['lymphocytes'][0],\n",
-    "                                               training_dataset.sample_references['lymphocytes'][1]])\n",
+    "training_batch = training_batch_sampler.batch([{'reference': training_dataset.sample_references['lymphocytes'][0]},\n",
+    "                                               {'reference': training_dataset.sample_references['lymphocytes'][1]}])\n",
     "x_batch, y_batch = training_batch"
    ]
   },
@@ -163,7 +184,7 @@
    "name": "python",
    "nbconvert_exporter": "python",
    "pygments_lexer": "ipython3",
-   "version": "3.8.11"
+   "version": "3.8.5"
   }
  },
  "nbformat": 4,
diff --git a/notebooks/SlidingWindow.ipynb b/notebooks/SlidingWindow.ipynb
index 45c79a4..b538de6 100644
--- a/notebooks/SlidingWindow.ipynb
+++ b/notebooks/SlidingWindow.ipynb
@@ -2,9 +2,28 @@
  "cells": [
   {
    "cell_type": "code",
-   "execution_count": 1,
+   "execution_count": 2,
    "metadata": {},
-   "outputs": [],
+   "outputs": [
+    {
+     "name": "stderr",
+     "output_type": "stream",
+     "text": [
+      "Downloading...\n",
+      "From: https://drive.google.com/uc?id=1noRtbC5fxBlnO7YnvktjIDhFI61PdOSB\n",
+      "To: /tmp/TCGA-21-5784-01Z-00-DX1.tif\n",
+      "100%|██████████| 363M/363M [00:20<00:00, 17.5MB/s] \n",
+      "Downloading...\n",
+      "From: https://drive.google.com/uc?id=1jkTp0IJHHpmLd1yDO1L3KRFJgm0STh0d\n",
+      "To: /tmp/TCGA-21-5784-01Z-00-DX1.xml\n",
+      "100%|██████████| 9.67k/9.67k [00:00<00:00, 1.87MB/s]\n",
+      "Downloading...\n",
+      "From: https://drive.google.com/uc?id=1nLdKzSLq79mon1RCevgEmG59E8Oq9JhZ\n",
+      "To: /tmp/TCGA-21-5784-01Z-00-DX1_tb_mask.tif\n",
+      "100%|██████████| 318k/318k [00:00<00:00, 3.91MB/s]\n"
+     ]
+    }
+   ],
    "source": [
     "# download example data\n",
     "# !pip install gdown\n",
@@ -14,7 +33,7 @@
   },
   {
    "cell_type": "code",
-   "execution_count": 2,
+   "execution_count": 1,
    "metadata": {},
    "outputs": [],
    "source": [
@@ -24,33 +43,34 @@
     "import time\n",
     "from pprint import pprint\n",
     "from tqdm.notebook import tqdm\n",
-    "from matplotlib import pyplot as plt"
+    "from matplotlib import pyplot as plt\n",
+    "import numpy as np"
    ]
   },
   {
    "cell_type": "code",
-   "execution_count": 3,
+   "execution_count": 2,
    "metadata": {},
    "outputs": [
     {
      "name": "stdout",
      "output_type": "stream",
      "text": [
-      "Creating: ./test2.tif....\n",
+      "Creating: ./slidingwindowtest2.tif....\n",
       "Spacing: 0.5\n",
-      "Dimensions: (36851, 25353)\n",
+      "Dimensions: (55216, 19812)\n",
       "Tile_shape: (1024, 1024)\n"
      ]
     },
     {
      "data": {
       "application/vnd.jupyter.widget-view+json": {
-       "model_id": "80d535b6c45f4a7c906d641e9f207067",
+       "model_id": "640c47eda0eb450e88b1c3bd70e02bb3",
        "version_major": 2,
        "version_minor": 0
       },
       "text/plain": [
-       "HBox(children=(HTML(value=''), FloatProgress(value=0.0, max=352.0), HTML(value='')))"
+       "HBox(children=(HTML(value=''), FloatProgress(value=0.0, max=104.0), HTML(value='')))"
       ]
      },
      "metadata": {},
@@ -77,10 +97,10 @@
     "tile_size = 1024\n",
     "output_size = 1030\n",
     "wsm_writer = WholeSlideMaskWriter()\n",
-    "with WholeSlideImage('/tmp/TCGA-21-5784-01Z-00-DX1.tif') as wsi:\n",
+    "with WholeSlideImage('/data/pathology/projects/breast-til-challenge/from-paper-lee-cooper-2019/data/wsis_tif_sp05/TCGA-A7-A6VY-01Z-00-DX1.38D4EBD7-40B0-4EE3-960A-1F00E8F83ADB.tif') as wsi:\n",
     "    shape = wsi.shapes[wsi.get_level_from_spacing(spacing)]\n",
-    "\n",
-    "wsm_writer.write(path='./test2.tif', spacing=spacing, dimensions=shape, tile_shape=(tile_size,tile_size))\n",
+    "    \n",
+    "wsm_writer.write(path='./slidingwindowtest2.tif', spacing=spacing, dimensions=shape, tile_shape=(tile_size,tile_size))\n",
     "for x_batch, y_batch, info in tqdm(training_iterator):\n",
     "    point = info['sample_references'][0]['point']\n",
     "    c, r = point.x-output_size//4, point.y-output_size//4\n",
@@ -141,20 +161,72 @@
    "cell_type": "code",
    "execution_count": 4,
    "metadata": {},
+   "outputs": [],
+   "source": [
+    "wsi = WholeSlideImage('/tmp/TCGA-A7-A6VY-01Z-00-DX1.38D4EBD7-40B0-4EE3-960A-1F00E8F83ADB.tif')"
+   ]
+  },
+  {
+   "cell_type": "code",
+   "execution_count": 5,
+   "metadata": {},
+   "outputs": [],
+   "source": [
+    "wsm = WholeSlideImage('/tmp/TCGA-A7-A6VY-01Z-00-DX1.38D4EBD7-40B0-4EE3-960A-1F00E8F83ADB_tissue.tif', backend='asap')"
+   ]
+  },
+  {
+   "cell_type": "code",
+   "execution_count": 10,
+   "metadata": {},
    "outputs": [
     {
      "data": {
       "text/plain": [
-       "1.5"
+       "((55216, 19812),\n",
+       " (27608, 9906),\n",
+       " (13804, 4953),\n",
+       " (6902, 2476),\n",
+       " (3451, 1238),\n",
+       " (1725, 619),\n",
+       " (862, 309),\n",
+       " (431, 154))"
       ]
      },
-     "execution_count": 4,
+     "execution_count": 10,
+     "metadata": {},
+     "output_type": "execute_result"
+    }
+   ],
+   "source": [
+    "wsi.shapes"
+   ]
+  },
+  {
+   "cell_type": "code",
+   "execution_count": 9,
+   "metadata": {},
+   "outputs": [
+    {
+     "data": {
+      "text/plain": [
+       "[(55216, 19812),\n",
+       " (27608, 9906),\n",
+       " (13804, 4953),\n",
+       " (6902, 2476),\n",
+       " (3451, 1238),\n",
+       " (1725, 619),\n",
+       " (862, 309),\n",
+       " (431, 154)]"
+      ]
+     },
+     "execution_count": 9,
      "metadata": {},
      "output_type": "execute_result"
     }
    ],
    "source": [
-    "3/2"
+    "wsm.shapes"
    ]
   },
   {
diff --git a/notebooks/configs/slidingwindowconfig.yml b/notebooks/configs/slidingwindowconfig.yml
index 17be79e..3f1f3d8 100644
--- a/notebooks/configs/slidingwindowconfig.yml
+++ b/notebooks/configs/slidingwindowconfig.yml
@@ -2,12 +2,17 @@ wholeslidedata:
     default:
         yaml_source: slidingwindowdata.yml
         
+        image_backend: openslide
+        
         batch_shape:
             batch_size: 1
             shape: [[1244, 1244, 3], [1244, 1244, 3]]
             y_shape: [2, 1030, 1030]
-            spacing: [0.5, 4.0]
-            
+            spacing: [0.5, 8.0]
+        
+        dataset:
+            copy_path: /tmp/
+        
         point_sampler:
             attribute: CenterPointSampler
           
diff --git a/notebooks/configs/slidingwindowdata.yml b/notebooks/configs/slidingwindowdata.yml
index 1775b44..4a0781c 100644
--- a/notebooks/configs/slidingwindowdata.yml
+++ b/notebooks/configs/slidingwindowdata.yml
@@ -1,5 +1,5 @@
 training:
     - wsi: 
-        path: /tmp/TCGA-21-5784-01Z-00-DX1.tif
+        path: /data/pathology/projects/breast-til-challenge/from-paper-lee-cooper-2019/data/wsis_tif_sp05/TCGA-A7-A6VY-01Z-00-DX1.38D4EBD7-40B0-4EE3-960A-1F00E8F83ADB.tif
       wsa: 
-        path: /tmp/TCGA-21-5784-01Z-00-DX1_tb_mask.tif
+        path: /data/pathology/projects/breast-til-challenge/from-paper-lee-cooper-2019/data/wsis_tif_tissue_masks_sp05/TCGA-A7-A6VY-01Z-00-DX1.38D4EBD7-40B0-4EE3-960A-1F00E8F83ADB_tissue.tif
diff --git a/wholeslidedata/configuration/presets/slidingwindow.yml b/wholeslidedata/configuration/presets/slidingwindow.yml
index 663338b..3ab32b8 100644
--- a/wholeslidedata/configuration/presets/slidingwindow.yml
+++ b/wholeslidedata/configuration/presets/slidingwindow.yml
@@ -4,7 +4,7 @@ default:
 
   annotation_parser: 
       attribute: MaskAnnotationParser
-      processing_spacing: 4.0
+      processing_spacing: 2.0
       
   label_map: 
       tissue: 1
diff --git a/wholeslidedata/dataset.py b/wholeslidedata/dataset.py
index 0e7b02e..4a2804a 100644
--- a/wholeslidedata/dataset.py
+++ b/wholeslidedata/dataset.py
@@ -2,7 +2,7 @@ import abc
 from collections import UserDict
 from dataclasses import dataclass
 from pprint import pformat
-from typing import Dict, Tuple
+from typing import Dict, Optional, Tuple, Union
 
 from wholeslidedata.annotation import utils as annotation_utils
 from wholeslidedata.labels import Labels
@@ -11,6 +11,31 @@ from wholeslidedata.source.associations import Associations
 from wholeslidedata.source.files import WholeSlideAnnotationFile, WholeSlideImageFile
 
 
+user_config = {
+    "wholeslidedata": {
+        "default": {
+            "yaml_source": "slidingwindowdata.yml",
+            "batch_shape": {
+                "batch_size": 1,
+                "shape": [[1244, 1244, 3], [1244, 1244, 3]],
+                "y_shape": [2, 1030, 1030],
+                "spacing": [0.5, 4.0],
+            },
+            "point_sampler": {"attribute": "CenterPointSampler"},
+            "patch_sampler": {"center": True},
+            "patch_label_sampler": {"center": True},
+            "sample_callbacks": [
+                {
+                    "module": "wholeslidedata.samplers.callbacks",
+                    "attribute": "FitOutput",
+                    "output_shape": [1030, 1030],
+                }
+            ],
+        }
+    }
+}
+
+
 @dataclass(frozen=True)
 class WholeSlideSampleReference:
     file_index: int
@@ -19,6 +44,8 @@ class WholeSlideSampleReference:
     annotation_index: int
 
 
+
+
 class DataSet(UserDict):
 
     IMAGES_IDENTIFIER = "images"
@@ -69,9 +96,9 @@ class DataSet(UserDict):
     def get_annotation_from_reference(
         self, sample_reference: WholeSlideSampleReference
     ):
-        return self.get_wsa_from_reference(sample_reference=sample_reference).annotations[
-            sample_reference.annotation_index
-        ]
+        return self.get_wsa_from_reference(
+            sample_reference=sample_reference
+        ).annotations[sample_reference.annotation_index]
 
     @abc.abstractmethod
     def _open(self, associations: Associations) -> dict:
@@ -178,6 +205,7 @@ class WholeSlideDataSet(DataSet):
                             annotation_index=annotation.index,
                         )
                     )
+
         return samples, all_samples
 
     def close_images(self):
@@ -279,4 +307,74 @@ class WholeSlideDataSet(DataSet):
                     if label not in counts_per_label_per_key_[file_key]:
                         counts_per_label_per_key_[file_key][label] = 0
                     counts_per_label_per_key_[file_key][label] += pixels
-        return counts_per_label_per_key_
\ No newline at end of file
+        return counts_per_label_per_key_
+
+
+# import cv2
+
+
+
+# # convert dataset to folder with images and cocostyle json 
+# # convert folder with images+cocostyle json to cocodataset
+# from wholeslidedata.samplers.patchsampler import PatchSampler
+# from wholeslidedata.samplers.samplesampler import SampleSampler
+# from wholeslidedata.samplers.patchlabelsampler import DetectionPatchLabelSampler
+# from pathlib import Path
+
+
+
+# def convert_dataset_to_coco_format(dataset: DataSet,
+#                                   licenses: Dict, 
+#                                   detection_labels,
+#                                   pixel_spacing,
+#                                   description: str, 
+#                                   url: str, 
+#                                   version: str, 
+#                                   output_folder: Union[str, Path]):    
+    
+#     coco_dataset = {}
+#     year = None
+#     date = None
+#     contributor = "Radboudumc"
+
+#     patch_sampler = PatchSampler()
+#     label_sampler = DetectionPatchLabelSampler(detection_labels=detection_labels)    
+#     sampler =  SampleSampler(patch_sampler, label_sampler, batch_shape=None)
+    
+#     images = {}
+#     annotations = {}
+
+#     id = 0
+#     for sample_references in dataset.sample_labels.values():
+#         for sample_reference in sample_references:
+#             wsi = dataset.get_image_from_reference(sample_reference)
+#             wsa = dataset.get_wsa_from_reference(sample_reference)
+#             annotation = dataset.get_annotation_from_reference(sample_reference)
+
+#             patch, objects = sampler._sample(*annotation.center, wsi, wsa, *annotation.size, pixel_spacing)
+#             file_name = id+wsi.path.stem+annotation.label.name+annotation.bounds+'.png'
+
+#             cv2.imwrite(file_name, patch)
+
+#             for object in objects:
+
+#         #     boxes = []
+#         #     for annotation in label:
+#         #         boxes.append({
+#         #             'id': id
+#         #             'category_id': annotation.label.value,
+#         #             'bbox': annotation.bounds,
+#         #         })
+
+#     #     save_boxes_to_annotations(boxes, file_name, id+image.path.stem+annotation.label.name+annotation.bounds+'.gt-png')
+#     #     image_record = {}
+#     #     image_record["file_name"] = image_path
+#     #     image_record["id"] = image_index
+#     #     image_record["height"] = shape[1]
+#     #     image_record["width"] = shape[0]
+
+#     # coco_dataset['images'] = images
+#     # coco_dataset["annotations"] = annotations
+
+
+#     # save_coco_json(cocodataset)
\ No newline at end of file
diff --git a/wholeslidedata/image/wholeslideimagewriter.py b/wholeslidedata/image/wholeslideimagewriter.py
index 891b45c..547a117 100644
--- a/wholeslidedata/image/wholeslideimagewriter.py
+++ b/wholeslidedata/image/wholeslideimagewriter.py
@@ -57,6 +57,9 @@ class Writer(abc.ABC):
     def __init__(self, callbacks=None):
         self._callbacks = callbacks
 
+    @abc.abstractmethod
+    def write(path, spacing, dimensions, tile_shape):
+        ...
 
 class WholeSlideImageWriter(Writer, MultiResolutionImageWriter):
     def __init__(self, callbacks=()):
diff --git a/wholeslidedata/samplers/patchlabelsampler.py b/wholeslidedata/samplers/patchlabelsampler.py
index c52a61e..6626791 100644
--- a/wholeslidedata/samplers/patchlabelsampler.py
+++ b/wholeslidedata/samplers/patchlabelsampler.py
@@ -1,260 +0,0 @@
-from typing import List, Optional
-
-import cv2
-import numpy as np
-from skimage.transform import resize
-from wholeslidedata.annotation.structures import Point, Polygon
-from wholeslidedata.samplers.utils import shift_coordinates
-from wholeslidedata.image.wholeslideimage import WholeSlideImage
-from wholeslidedata.samplers.sampler import Sampler
-
-
-class PatchLabelSampler(Sampler):
-    """[summary]
-
-    Args:
-        Sampler ([type]): [description]
-
-    Raises:
-        ValueError: [description]
-
-    Returns:
-        [type]: [description]
-    """
-
-    def sample(
-        self,
-        wsa,
-        point: Point,
-        size,
-        ratio,
-    ):
-        """[summary]
-
-        Args:
-            wsa ([type]): [description]
-            point ([type]): [description]
-            size ([type]): [description]
-            ratio ([type]): [description]
-
-        Raises:
-            ValueError: [description]
-
-        Returns:
-            [type]: [description]
-        """
-
-    def resolve_batch(y_batch):
-        pass
-
-
-@PatchLabelSampler.register(("mask",))
-class MaskPatchLabelSampler(PatchLabelSampler):
-    def __init__(self, image_backend, ratio, center, relative):
-        self._image_backend = image_backend
-        self._ratio = ratio
-        self._center =center
-        self._relative = relative
-
-    # annotation should be coupled to image_annotation. how?
-    def sample(
-        self,
-        wsa,
-        point,
-        size,
-        ratio,
-    ):
-        x, y = point.x, point.y
-        width, height = size
-        mask = WholeSlideImage(wsa.path, backend=self._image_backend)
-        spacing = mask.spacings[0]
-
-        mask_patch = np.array(
-            mask.get_patch(
-                int(x // self._ratio),
-                int(y // self._ratio),
-                int(width // self._ratio),
-                int(height // self._ratio),
-                spacing=spacing,
-                center=self._center,
-                relative=self._relative,
-            )
-        )[..., 0]
-
-        mask.close()
-        mask = None
-        del mask
-
-        # upscale
-        if self._ratio > 1:
-            mask_patch = resize(
-                mask_patch.squeeze().astype("uint8"),
-                size,                
-                order=0,
-                preserve_range=True,
-            )
-
-        return mask_patch.astype(np.uint8)
-
-    def resolve_batch(y_batch):
-        pass
-
-
-@PatchLabelSampler.register(("segmentation",))
-class SegmentationPatchLabelSampler(PatchLabelSampler):
-    def __init__(self):
-        pass
-
-    # annotation should be coupled to image_annotation. how?
-    def sample(
-        self,
-        wsa,
-        point,
-        size,
-        ratio,
-    ):
-        center_x, center_y = point.x, point.y
-        width, height = size
-
-        # get annotations
-        annotations = wsa.select_annotations(
-            center_x, center_y, (width * ratio) - 1, (height * ratio) - 1
-        )
-
-        # create mask placeholder
-        mask = np.zeros((height, width), dtype=np.int32)
-        # set labels of all selected annotations
-        for annotation in annotations:
-            coordinates = np.copy(annotation.coordinates)
-            coordinates = shift_coordinates(
-                coordinates, center_x, center_y, width, height, ratio
-            )
-
-            if isinstance(annotation, Polygon):
-                holemask = np.ones((width, height), dtype=np.int32) * -1
-                for hole in annotation.holes:
-                    hcoordinates = shift_coordinates(
-                        hole, center_x, center_y, width, height, ratio
-                    )
-                    cv2.fillPoly(holemask, np.array([hcoordinates], dtype=np.int32), 1)
-                    holemask[holemask != -1] = mask[holemask != -1]
-                cv2.fillPoly(
-                    mask,
-                    np.array([coordinates], dtype=np.int32),
-                    annotation.label.value,
-                )
-                mask[holemask != -1] = holemask[holemask != -1]
-
-            elif isinstance(annotation, Point):
-                mask[int(coordinates[1]), int(coordinates[0])] = annotation.label.value
-
-        return mask.astype(np.uint8)
-
-
-@PatchLabelSampler.register(("classification",))
-class ClassificationPatchLabelSampler(PatchLabelSampler):
-    def __init__(self):
-        pass
-
-    def sample(
-        self,
-        wsa,
-        point,
-        size,
-        ratio,
-    ):
-        center_x, center_y = point.x, point.y
-
-        # get annotations
-        annotations = wsa.select_annotations(center_x, center_y, 1, 1)
-
-        return np.array([annotations[-1].label.value])
-
-
-@PatchLabelSampler.register(("detection",))
-class DetectionPatchLabelSampler(PatchLabelSampler):
-    def __init__(
-        self,
-        max_number_objects: int = None,
-        detection_labels: List[str] = None,
-        point_box_sizes: Optional[dict] = None,
-    ):
-        self._max_number_objects = max_number_objects
-        self._point_box_sizes = point_box_sizes
-        self._detection_labels = detection_labels
-
-    def sample(
-        self,
-        wsa,
-        point,
-        size,
-        ratio,
-    ):
-        center_x, center_y = point.x, point.y
-        width, height = size
-
-        # Get annotations
-        annotations = wsa.select_annotations(
-            center_x, center_y, (width * ratio) - 1, (height * ratio) - 1
-        )
-
-        max_number_objects = self._max_number_objects or width * height
-        if len(annotations) > max_number_objects:
-            raise ValueError(
-                f"to many objects in ground truth: {len(annotations)} with possible max number of objects: {max_number_objects}"
-            )
-
-        objects = np.zeros((max_number_objects, 6))
-        idx = 0
-        for annotation in annotations:
-            if self._detection_labels is not None:
-                if annotation.label.name not in self._detection_labels:
-                    continue
-
-            if isinstance(annotation, Point):
-                objects[idx][:4] = self._get_point_coordinates(
-                    annotation, center_x, center_y, width, height, ratio
-                )
-
-            if isinstance(annotation, Polygon):
-                objects[idx][:4] = self._get_polygon_coordinates(
-                    annotation, center_x, center_y, width, height, ratio
-                )
-
-            objects[idx][4] = annotation.label.value
-            objects[idx][5] = 1  # confidence
-            idx += 1
-        return objects
-
-    def _get_point_coordinates(
-        self, annotation, center_x, center_y, width, height, ratio
-    ):
-        coordinates = shift_coordinates(
-            annotation.coordinates, center_x, center_y, width, height, ratio
-        )
-
-        size = 0
-        if self._point_box_sizes is not None:
-            size = np.array(self._point_box_sizes[annotation.label.name])
-
-        x1 = int(max(0, coordinates[0] - (size // 2)))
-        y1 = int(max(0, coordinates[1] - (size // 2)))
-        x2 = int(min(width-1, coordinates[0] + (size // 2)))
-        y2 = int(min(height-1, coordinates[1] + (size // 2)))
-
-        return x1, y1, x2, y2
-
-    def _get_polygon_coordinates(
-        self, annotation, center_x, center_y, width, height, ratio
-    ):
-        coordinates = [annotation.bounds[:2], annotation.bounds[2:]]
-        coordinates = np.array(coordinates, dtype="float")
-        coordinates = shift_coordinates(
-            coordinates, center_x, center_y, width, height, ratio
-        )
-        x1 = max(0, coordinates[0][0])
-        y1 = max(0, coordinates[0][1])
-        x2 = min(height-1, coordinates[1][0])
-        y2 = min(width-1, coordinates[1][1])
-
-        return x1, y1, x2, y2
diff --git a/wholeslidedata/samplers/samplesampler.py b/wholeslidedata/samplers/samplesampler.py
index 937f6a7..6c5ecf0 100644
--- a/wholeslidedata/samplers/samplesampler.py
+++ b/wholeslidedata/samplers/samplesampler.py
@@ -1,4 +1,4 @@
-from typing import List
+from typing import List, Union
 
 from wholeslidedata.annotation.structures import Annotation
 from wholeslidedata.annotation.wholeslideannotation import WholeSlideAnnotation
@@ -44,7 +44,7 @@ class SampleSampler:
         point: tuple,
         wsi: WholeSlideImage,
         wsa: WholeSlideAnnotation,
-        patch_shape,
+        patch_shape: Union[tuple, list],
         pixel_spacing: float,
     ):
 
