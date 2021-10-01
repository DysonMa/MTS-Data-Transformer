# MTS Specimens Data Transformer

https://github.com/DysonMa/MTS-Data-Transformer

>This program is designed for graduate students who are currently studying at the NTU CE 812 lab.

## What did this program solve?

Traditionally, we use Excel as our data processing tool to calculate Elastic Modulus with linear regression, and find maximum compressive strength with functions in Excel manaully. 

Now, with this program, you can save the time of manual calculation and quickly get experimental data results by the exe build by PyQt5!

## How to get it?

- use `git` command to clone this repo
- [Download as zip](https://github.com/DysonMa/MTS-Data-Transformer/archive/refs/heads/main.zip)
 
## Environment

- You don't need to install Python to execute `ElasticModulus_Test-UI.exe`
- Support both Windows and Linux

## Packages

- matplotlib, seaborn
- PyQt5
- Pandas
- Numpy
- Scipy
- Xlsxwriter

## Folder Structure

- `datas`: datas comes from MTS
- `EM_Test_Final`: `ElasticModulus_Test-UI.exe` is the only file you need to care about
- `pictures`: for demo pictures
- `src`: main code(not designed very well, maybe refactor it in the future)
- `output`: All the datas and plots are listed in this folder according to the folder name you named

## How to use it?

1. Open the exe in the `EM_Test_Final` folder
2. Click `ElasticModulus_Test-UI.exe` to start the program
3. Initial picture looks like this 

    ![demo1](./pictures/demo1.PNG)

4. Click `Select` button on the upper left of the window to choose any file from MTS

    > Choose `specimen.txt` for demo

5. Choose specimen size(`Cube` or `Cylinder`)

    > Choose `Cylinder` for demo

6. Key in a number for `配比種類數量` which means the numbers of ratio type 

    > **<p.s> The value of this field must be the same as the number of `配比種類數量`** 

    The datas below are just for demo, DO NOT take it seriously ^0^: 
    |配比種類|配比數量|
    |:--:|:--:|
    |0.25|5|
    |0.35|5|
    |0.45|5|
    |0.55|5|
    |0.87|3|

7. Select a folder in `選擇檔案欲存入的位置` to save the output files

    > Select `output` folder for demo

8. Enter the save folder name in `輸入存檔名稱`
    > Enter `WTF_MTS` for demo

9. Click `Plot and Export to Excel` button to start the journey!

    ![demo2](./pictures/demo2.PNG)

10. Change to `預覽數據` page for detail

    ![demo3](./pictures/demo3.PNG)

11. All the datas and figures are stored in save folder, i.e. `WTF_MTS`

## Contact

It's not designed very well and still exist some bugs to fix, so feel free to contact me if needed

- Author: madihsiang (R07)
- Gmail: madihsiang@gmail.com

## Happy Experiment!