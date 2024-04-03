#! /bin/bash

cd /public/labdata/lincha/alps/adni3/ADNI_0/
ls > id.txt
head -n -1 id.txt > tmp.txt && mv tmp.txt id.txt

mkdir sort
mkdir V1
mkdir png
cat id.txt |while read id
do
 cd /public/labdata/lincha/alps/adni3/ADNI_0/${id}/*/
 ls > day.txt
 head -n -1 day.txt > tmp.txt && mv tmp.txt day.txt
 
 cat day.txt | while read day
 do
  cd /public/labdata/lincha/alps/adni3/ADNI_0/${id}/*/${day}/
  ls > image.txt
  head -n -1 image.txt > tmp.txt && mv tmp.txt image.txt
  
  cat image.txt | while read image
  do
   cd /public/labdata/lincha/alps/adni3/ADNI_0/${id}/*/${day}/
   dcm2niix ./${image}
   cd /public/labdata/lincha/alps/adni3/ADNI_0/${id}/*/${day}/${image}/
   mv *.nii ${image}.nii
   mv *.bval ${image}.bval
   mv *.bvec ${image}.bvec
   mv *.json ${image}.json
   mkdir /public/labdata/lincha/alps/adni3/ADNI_0/sort/${image}
   mv ${image}* /public/labdata/lincha/alps/adni3/ADNI_0/sort/${image}/
   cd /public/labdata/lincha/alps/adni3/ADNI_0/sort/${image}/
   fslroi ${image}.nii ${image}_b0.nii 0 1
   bet ${image}_b0.nii.gz ${image}_b0_brain.nii.gz -R -m -f 0.3
   dtifit --data=${image}.nii --out=${image} --mask=${image}_b0_brain_mask.nii.gz --bvecs=${image}.bvec --bvals=${image}.bval --save_tensor
   fslsplit ${image}_tensor.nii.gz 
   cp ${image}_V1.nii.gz /public/labdata/lincha/alps/adni3/ADNI_0/V1/
  done
 done
done


cd /public/labdata/lincha/alps/adni3/ADNI_0/V1
ls > id.txt
sed -i 's/_V1.nii.gz//g' id.txt
head -n -1 id.txt > tmp.txt && mv tmp.txt id.txt
truncate -s -1 id.txt

python /public/labdata/lincha/nii2png.py
rm *.txt 
mv *.png /public/labdata/lincha/alps/adni3/ADNI_0/png/


