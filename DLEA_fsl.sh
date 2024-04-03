
echo "filename,value1,value2,value3,value4,value5,value6,value7,value8" > /home/lincha/tem4/gpmp/output.csv
tail -n +2 /home/lincha/tem4/gpmp/output_boundary_coordinates.csv | while IFS=, read -r filename xmin_0 ymin_0 xmax_0 ymax_0 green_max_0 blue_min_0 xmin_1 ymin_1 xmax_1 ymax_1 blue_max_1 green_min_1; do
    if [ $(echo "$xmin_0 $ymin_0 $xmax_0 $ymax_0 $green_max_0 $blue_min_0 0 6" | awk '{if ($1 == 0 && $2 == 0 && $3 == 0 && $4 == 0 && $5 == 0 && $6 == 0) print 1; else print 0}') -eq 1 ]; then
        value1=0
        value2=0
        value3=0
        value4=0
    else
        xmin_r1=$(echo "$xmin_0 + $blue_min_0 + 1"| bc)
        xmin_r2=$(echo "$xmin_0 + 1"| bc)
        xsize_r1=$(echo "$xmax_0 - $blue_min_0 - $xmin_0 + 1"| bc)
        xsize_r2=$(echo "$green_max_0 + 1"| bc)
        roi_r2_height=$(echo "$ymax_0 - $ymin_0" | bc)
        roi_r1_height=$(echo "$ymax_0 - $ymin_0" | bc)
        ymin=$(echo "$ymin_0 + 1" | bc)
        zmin=$(echo "$filename" | grep -oP '\d+(?=\.[^.]+$)')
        id=$(echo "$filename" | grep -oP '^[^_]+')
        cd /public/labdata/lincha/PD_ImagingFromSYSU_1st/PD_MRI/sorted/${id}
        rm ${id}_FA_mask*
        fslmaths ${id}_FA.nii.gz -roi ${xmin_r1} ${xsize_r1} ${ymin} ${roi_r1_height} ${zmin} 3 0 1 ${id}_FA_mask_r1.nii.gz
        fslmaths ${id}_FA.nii.gz -roi ${xmin_r2} ${xsize_r2} ${ymin} ${roi_r2_height} ${zmin} 3 0 1 ${id}_FA_mask_r2.nii.gz
        fslmaths ${id}_FA_mask_r1.nii.gz -bin ${id}_FA_mask_r1_bin.nii.gz
        fslmaths ${id}_FA_mask_r2.nii.gz -bin ${id}_FA_mask_r2_bin.nii.gz
        value1=$(fslstats vol0000.nii.gz -k ${id}_FA_mask_r1_bin.nii.gz -M)
        value2=$(fslstats vol0000.nii.gz -k ${id}_FA_mask_r2_bin.nii.gz -M)
        value3=$(fslstats vol0003.nii.gz -k ${id}_FA_mask_r1_bin.nii.gz -M)
        value4=$(fslstats vol0005.nii.gz -k ${id}_FA_mask_r2_bin.nii.gz -M)
        rm ${id}_FA_mask*
    fi

    if [ $(echo "$xmin_1 $ymin_1 $xmax_1 $ymax_1 $blue_max_1 $green_min_1 0 6" | awk '{if ($1 == 0 && $2 == 0 && $3 == 0 && $4 == 0 && $5 == 0 && $6 == 0) print 1; else print 0}') -eq 1 ]; then
        value5=0
        value6=0
        value7=0
        value8=0
    else
        xmin_l2=$(echo "$xmin_1 + $green_min_1 + 1"| bc)
        xmin_l1=$(echo "$xmin_1 + 1"| bc)
        xsize_l2=$(echo "$xmax_1 - $green_min_1 - $xmin_1 + 1|" bc)
        xsize_l1=$(echo "$blue_max_1 + 1|" bc)
        roi_l1_height=$(echo "$ymax_1 - $ymin_1" | bc)
        roi_l2_height=$(echo "$ymax_1 - $ymin_1" | bc)
        ymin=$(echo "$ymin_0 + 1" | bc)
        zmin=$(echo "$filename" | grep -oP '\d+(?=\.[^.]+$)')
        id=$(echo "$filename" | grep -oP '^[^_]+')
        zmin=$(echo "$filename" | grep -oP '\d+(?=\.[^.]+$)')
        cd /public/labdata/lincha/PD_ImagingFromSYSU_1st/PD_MRI/sorted/${id}
        rm ${id}_FA_mask*
        fslmaths ${id}_FA.nii.gz -roi ${xmin_l1} ${xsize_l1} ${ymin} ${roi_l1_height} ${zmin} 3 0 1 ${id}_FA_mask_l1.nii.gz
        fslmaths ${id}_FA.nii.gz -roi ${xmin_l2} ${xsize_l2} ${ymin} ${roi_l2_height} ${zmin} 3 0 1 ${id}_FA_mask_l2.nii.gz
        fslmaths ${id}_FA_mask_l1.nii.gz -bin ${id}_FA_mask_l1_bin.nii.gz
        fslmaths ${id}_FA_mask_l2.nii.gz -bin ${id}_FA_mask_l2_bin.nii.gz
        value5=$(fslstats vol0000.nii.gz -k ${id}_FA_mask_l1_bin.nii.gz -M)
        value6=$(fslstats vol0000.nii.gz -k ${id}_FA_mask_l2_bin.nii.gz -M)
        value7=$(fslstats vol0003.nii.gz -k ${id}_FA_mask_l1_bin.nii.gz -M)
        value8=$(fslstats vol0005.nii.gz -k ${id}_FA_mask_l2_bin.nii.gz -M)
        rm ${id}_FA_mask*
    fi

    # 写入结果到 output.csv
    echo "$filename,$value1,$value2,$value3,$value4,$value5,$value6,$value7,$value8" >> /home/lincha/tem4/gpmp/output.csv
done


