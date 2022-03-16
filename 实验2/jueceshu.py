import numpy as np
from math import log
import operator
import matplotlib.pyplot as plt
##读取训练集和测试集
TrainData = np.loadtxt("./traindata.txt")
TestData = np.loadtxt("./testdata.txt")
decisionNode = dict(boxstyle="sawtooth", fc="0.8")
leafNode = dict(boxstyle="round4", fc="0.9")
arrow_args = dict(arrowstyle="<-")

###计算信息熵
def CalEntropy(index, label , step):
    kind = [0 for i in range(3)]
    Entropy = 0
    p = [0 for i in range(3)]
    for i in range(step):
        if label[index[i]] == 1:
            kind[0] += 1
        elif label[index[i]] == 2:
            kind[1] += 1
        else:
            kind[2] += 1
    for i in range(3):
        p[i] = kind[i] / len(label)##每一分类的概率
        if p[i] != 0:
            Entropy -= p[i] * log(p[i] , 2)
    return Entropy

def bestFeature(dataSet):
    index = []
    for n in range(4):
        index.append(np.argsort(dataSet[:, n], axis=0))
    EntD = CalEntropy(range(len(dataSet[:, 0])), dataSet[:, -1], len(dataSet[:, 0]))
    T = [[], [], [], []]  # 4个连续属性的候选划分点
    Gain = [[], [], [], []]  # 4个连续属性的候选增益
    for n in range(len(dataSet[:, -1]) - 1):
        for i in range(4):
            T[i].append((dataSet[index[i][n], i] + dataSet[index[i][n + 1], i]) / 2)
            EntDv = [0, 0]
            for j in range(len(dataSet[:, 0]) - 1):
                EntDv[0] = CalEntropy(index[i][:j + 1], dataSet[:, -1], j + 1)
                EntDv[1] = CalEntropy(index[i][j + 1:], dataSet[:, -1], len(index[i][j + 1:]))
                Gain[i].append(EntD - ((j + 1) / (len(dataSet[:, 0]) - 1)) * EntDv[0] - (
                        ((len(dataSet[:, 0]) - 1) - (j + 1)) / (len(dataSet[:, 0]) - 1)) * EntDv[1])
    MAX_Gain = [0, 0, 0, 0]
    MAX_index = [0, 0, 0, 0]
    for n in range(4):
        MAX_Gain[n] = max(Gain[n])
        MAX_index[n] = T[n][Gain[n].index(max(Gain[n]))]
    # 最大增益 划分值 所在的属性列
    return max(MAX_Gain), MAX_index[MAX_Gain.index(max(MAX_Gain))], MAX_Gain.index(max(MAX_Gain))



def DivideData(data, value , line):# 根据求得的最大增益，属性，划分值，划分数据集
    smallDataSet = np.empty(shape=(0,5))
    largeDataSet = np.empty(shape=(0,5))
    for i in range(len(data[:, -1])):
        if data[i,line] < value:
            smallDataSet = np.append(smallDataSet, [data[i, :]], axis=0)
        else:
            largeDataSet = np.append(largeDataSet, [data[i, :]], axis=0)
    return smallDataSet, largeDataSet

def Most(LabelList):
    Count = dict()
    for i in LabelList:
        if i not in Count.keys():
            Count[i] = 0
        Count[i] += 1
    SortedCount = sorted(Count.iteritems(),  key=operator.itemgetter(1), reverse=True)
    return SortedCount

def CreateTree(data):
    LabelList = data[:,-1].tolist()
    if LabelList.count(LabelList[0]) == len(LabelList):
        return LabelList[0]  ###当标签完全一样时直接返回
    if len(data[0]) == 1:
        return Most(LabelList)###遍历完所有的标签返回出现次数最多的标签
    MaxGain , value , line = bestFeature(data)
    MyTree = {line:{}}
    small , large = DivideData(data,value,line)
    MyTree[line]["-" + str(value)] = CreateTree(small)
    MyTree[line]["+" + str(value)] = CreateTree(large)
    return MyTree

def GetNumLeaf(Mytree):
    num = 0
    firstStr = list(Mytree.keys())[0]
    secondDict = Mytree[firstStr]
    for key in secondDict.keys():
        # 测试节点的数据类型是否为字典
        if type(secondDict[key]).__name__ == 'dict':
            num += GetNumLeaf(secondDict[key])
        else:
            num += 1
    return num
def GetDepth(Mytree):
    Depth = 0
    firstStr = list(Mytree.keys())[0]
    secondDict = Mytree[firstStr]
    for key in secondDict.keys():
        if type(secondDict[key]).__name__ == 'dict':
            NowDepth = 1 + GetDepth(secondDict[key])
        else:
            NowDepth = 1
        if NowDepth > Depth: Depth = NowDepth
    return Depth
def plotNode(nodeTxt, centerPt, parentPt, nodeType):
    createPlot.ax1.annotate(nodeTxt, xy=parentPt, xycoords='axes fraction',
                            xytext=centerPt, textcoords='axes fraction',
                            va="center", ha="center", bbox=nodeType, arrowprops=arrow_args)
# 在父子节点中填充文本信息
def plotMidText(cntrPt, parentPt, txtString):
    xMid = (parentPt[0] - cntrPt[0]) / 2.0 + cntrPt[0]
    yMid = (parentPt[1] - cntrPt[1]) / 2.0 + cntrPt[1]
    createPlot.ax1.text(xMid, yMid, txtString, va="center", ha="center", rotation=30)
def plotTree(myTree, parentPt, nodeTxt):
    # 计算宽和高
    numLeafs = GetNumLeaf(myTree)
    depth = GetDepth(myTree)
    firstStr = list(myTree.keys())[0]
    cntrPt = (plotTree.xOff + (1.0 + float(numLeafs)) / 2.0 / plotTree.totalW, plotTree.yOff)
    # 标记子节点属性值
    plotMidText(cntrPt, parentPt, nodeTxt)
    plotNode(firstStr, cntrPt, parentPt, decisionNode)
    secondDict = myTree[firstStr]
    # 减小y偏移
    plotTree.yOff = plotTree.yOff - 1.0 / plotTree.totalD
    for key in secondDict.keys():
        if type(secondDict[key]).__name__ == 'dict':
            plotTree(secondDict[key], cntrPt, str(key))
        else:
            plotTree.xOff = plotTree.xOff + 1.0 / plotTree.totalW
            plotNode(secondDict[key], (plotTree.xOff, plotTree.yOff), cntrPt, leafNode)
            plotMidText((plotTree.xOff, plotTree.yOff), cntrPt, str(key))
    plotTree.yOff = plotTree.yOff + 1.0 / plotTree.totalD
def createPlot(inTree):
    fig = plt.figure(1, facecolor='white')
    fig.clf()
    axprops = dict(xticks=[], yticks=[])
    createPlot.ax1 = plt.subplot(111, frameon=False, **axprops)
    plotTree.totalW = float(GetNumLeaf(inTree))
    plotTree.totalD = float(GetDepth(inTree))
    plotTree.xOff = -0.5 / plotTree.totalW;
    plotTree.yOff = 1.0;
    plotTree(inTree, (0.5, 1.0), '')
    plt.show()

def retrieveTree(i):
    listOfTrees = [{'no surfacing': {0: 'no', 1: {'flippers': {0: 'no', 1: 'yes'}}}},
                   {'no surfacing': {0: 'no', 1: {'flippers': {0: {'head': {0: 'no', 1: 'yes'}}, 1: 'no'}}}}
                   ]
    return listOfTrees[i]

def Classify(Mytree, TestData):
    firstStr = list(Mytree.keys())[0]
    secondDict = Mytree[firstStr]
    test = TestData
    FeaIndex = [0,1,2,3].index(firstStr)
    for i in list(secondDict.keys()):
        if float(i) < 0:
            if test[FeaIndex] <= -float(i):
                if type(secondDict[i]).__name__ == 'dict':
                    classLabel = Classify(secondDict[i], test)
                else:
                    classLabel = secondDict[i]
        else:
            if test[FeaIndex] >= float(i):
                if type(secondDict[i]).__name__ == 'dict':
                    classLabel = Classify(secondDict[i], test)
                else:
                    classLabel = secondDict[i]
    return classLabel

RightResult = 1
Mytree = CreateTree(TrainData)
for i in range(len(TestData[:, -1])):
    if Classify(Mytree, TestData[i, :]) == TestData[i, -1]:
        RightResult += 1
##绘制决策树
Mytree.update({'feature-3':Mytree.pop(2)})
Mytree["feature-3"].update({'<2.45':Mytree["feature-3"].pop("-2.45")})
Mytree["feature-3"].update({'>=2.45':Mytree["feature-3"].pop("+2.45")})
Mytree["feature-3"]['<2.45'] = "label-1"
Mytree['feature-3']['>=2.45'].update({'feature-3':Mytree['feature-3']['>=2.45'].pop(2)})
Mytree['feature-3']['>=2.45']['feature-3'].update({'<4.8':Mytree['feature-3']['>=2.45']['feature-3'].pop("-4.8")})
Mytree['feature-3']['>=2.45']['feature-3'].update({'>=4.8':Mytree['feature-3']['>=2.45']['feature-3'].pop("+4.8")})
Mytree['feature-3']['>=2.45']['feature-3']["<4.8"]= "label-2"
Mytree['feature-3']['>=2.45']["feature-3"][">=4.8"].update({'feature-4':Mytree['feature-3']['>=2.45']["feature-3"][">=4.8"].pop(3)})
Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]['feature-4'].update({'<1.75':Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]['feature-4'].pop("-1.75")})
Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]['feature-4'].update({'>=1.75':Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]['feature-4'].pop("+1.75")})
Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]["feature-4"][">=1.75"]= "label-3"
Mytree['feature-3']['>=2.45']["feature-3"][">=4.8"]["feature-4"]['<1.75'].update({'feature-3':Mytree['feature-3']['>=2.45']["feature-3"][">=4.8"]["feature-4"]['<1.75'].pop(2)})
Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]['feature-4']['<1.75']["feature-3"].update({'<5.1':Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]['feature-4']['<1.75']["feature-3"].pop("-5.1")})
Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]['feature-4']['<1.75']["feature-3"].update({'>=5.1':Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]['feature-4']['<1.75']["feature-3"].pop("+5.1")})
Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]["feature-4"]["<1.75"]["feature-3"]["<5.1"]= "label-2"
Mytree['feature-3']['>=2.45']["feature-3"][">=4.8"]["feature-4"]['<1.75']["feature-3"][">=5.1"].update({'feature-1':Mytree['feature-3']['>=2.45']["feature-3"][">=4.8"]["feature-4"]['<1.75']["feature-3"][">=5.1"].pop(0)})
Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]['feature-4']['<1.75']["feature-3"][">=5.1"]["feature-1"].update({'<6.05':Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]['feature-4']['<1.75']["feature-3"][">=5.1"]["feature-1"].pop("-6.05")})
Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]['feature-4']['<1.75']["feature-3"][">=5.1"]["feature-1"].update({'>=6.05':Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]['feature-4']['<1.75']["feature-3"][">=5.1"]["feature-1"].pop("+6.05")})
Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]["feature-4"]["<1.75"]["feature-3"][">=5.1"]["feature-1"]["<6.05"]= "label-2"
Mytree['feature-3']['>=2.45']['feature-3'][">=4.8"]["feature-4"]["<1.75"]["feature-3"][">=5.1"]["feature-1"][">=6.05"]= "label-3"
print("决策树为：")
print(Mytree)
print("分类准确率为：",str(100 * RightResult/len(TestData[:, -1])) + " %")
createPlot(Mytree)