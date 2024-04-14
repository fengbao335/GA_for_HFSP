import random
import numpy as np
import copy
from Scheduling import Scheduling as Sch
from Instance import Job, State, Machine, PT
import matplotlib.pyplot as plt


class GA:
    def __init__(self, J_num, State, Machine, PT):
        # 初始化遗传算法类
        self.State = State  # 状态信息
        self.Machine = Machine  # 机器信息
        self.PT = PT  # 加工时间信息
        self.J_num = J_num  # 作业数量
        self.Pm = 0.2  # 变异概率
        self.Pc = 0.9  # 交叉概率
        self.Pop_size = 100  # 种群大小

    # 随机产生染色体
    def RCH(self):
        # 染色体表示作业的排列顺序
        Chromo = [i for i in range(self.J_num)]  # 初始化染色体为作业编号的列表
        random.shuffle(Chromo)  # 随机打乱作业顺序
        return Chromo

        # 生成初始种群

    def CHS(self):
        # 初始化种群，种群由多个染色体组成
        CHS = []
        for i in range(self.Pop_size):
            CHS.append(self.RCH())  # 为每个个体生成一个随机染色体
        return CHS

        # 选择

    def Select(self, Fit_value):
        # 根据适应度值进行选择操作
        Fit = []
        for i in range(len(Fit_value)):
            fit = 1 / Fit_value[i]  # 计算适应度（这里假设适应度与目标函数值成反比）
            Fit.append(fit)
        Fit = np.array(Fit)
        # 根据适应度值进行轮盘赌选择
        idx = np.random.choice(np.arange(len(Fit_value)), size=len(Fit_value), replace=True,
                               p=(Fit) / (Fit.sum()))
        return idx

        # 交叉

    def Crossover(self, CHS1, CHS2):
        # 交叉操作，生成新的染色体
        T_r = [j for j in range(self.J_num)]  # 初始化一个与作业数量相同的列表
        r = random.randint(2, self.J_num)  # 随机选择交叉点位置
        random.shuffle(T_r)
        R = T_r[0:r]  # 选择交叉点位置前的r个作业
        # 将父代的染色体复制到子代中去，保持他们的顺序和位置
        H1 = [CHS1[_] for _ in R]
        H2 = [CHS2[_] for _ in R]
        C1 = [_ for _ in CHS1 if _ not in H2]  # 父代1中不在H2中的作业
        C2 = [_ for _ in CHS2 if _ not in H1]  # 父代2中不在H1中的作业
        CHS1, CHS2 = [], []  # 初始化新的子代染色体
        k, m = 0, 0  # 计数器
        for i in range(self.J_num):
            if i not in R:
                CHS1.append(C1[k])
                CHS2.append(C2[k])
                k += 1
            else:
                CHS1.append(H2[m])
                CHS2.append(H1[m])
                m += 1
        return CHS1, CHS2

        # 变异

    def Mutation(self, CHS):
        # 变异操作，用于改变染色体中的部分基因
        Tr = [i_num for i_num in range(self.J_num)]  # 创建一个从0到作业数J_num-1的整数列表，用于后续选择变异的位置
        # 注意：这里的变异操作看起来有些混乱，它并没有真正改变染色体中的基因，只是进行了位置的重新排列
        # 这可能并不是传统意义上的变异操作，可能需要根据具体问题调整。
        r = random.randint(1, self.J_num)  # 随机选择要进行变异的作业位置数量
        random.shuffle(Tr)  # 打乱整数列表Tr的顺序
        T_r = Tr[0:r]  # 从打乱后的列表中选取前r个位置作为变异位置
        K = []  # 初始化一个空列表，用于存放变异后的作业顺序
        for i in T_r:
            K.append(CHS[i])  # 将选中的变异位置的作业添加到K列表中
        random.shuffle(K)  # 打乱K列表中的作业顺序
        k = 0
        for i in T_r:
            CHS[i] = K[k]  # 将打乱后的作业顺序重新放回原染色体中
            k += 1
        return CHS  # 返回变异后的染色体

    def main(self):
        BF = []  # 初始化一个空列表，用于存储每一代的最佳适应度值
        x = [_ for _ in range(self.Pop_size + 1)]  # 创建一个从0到种群大小Pop_size的整数列表，用于绘制适应度曲线的x轴坐标
        C = self.CHS()  # 调用CHS方法生成初始种群
        Fit = []  # 初始化一个空列表，用于存储种群中每个染色体的适应度值

        # 计算初始种群的适应度值
        for C_i in C:
            s = Sch(self.J_num, self.Machine, self.State, self.PT)  # 创建一个作业调度对象
            s.Decode(C_i)  # 调用Decode方法解码染色体，得到作业调度方案
            Fit.append(s.fitness)  # 计算染色体的适应度值，并添加到Fit列表中

        best_C = None  # 初始化最优解的染色体为None
        best_fit = min(Fit)  # 计算初始种群中的最小适应度值，作为当前最优适应度值
        BF.append(best_fit)  # 将初始最优适应度值添加到BF列表中

        # 迭代更新种群
        for i in range(self.Pop_size):  # 这里应该是迭代Generation次，而不是Pop_size次，这里可能是个错误
            # 选择操作
            C_id = self.Select(Fit)  # 调用Select方法根据适应度值进行选择操作，返回被选中染色体的索引
            C = [C[_] for _ in C_id]  # 根据索引重新构建种群

            # 交叉和变异操作
            for Ci in range(len(C)):
                if random.random() < self.Pc:  # 如果生成的随机数小于交叉概率Pc
                    _C = [C[Ci]]  # 创建一个临时列表，用于存放当前染色体及其子代
                    CHS1, CHS2 = self.Crossover(C[Ci], random.choice(C))  # 对当前染色体和随机选择的另一个染色体进行交叉操作，生成两个子代
                    _C.extend([CHS1, CHS2])  # 将两个子代添加到临时列表中

                    # 计算子代的适应度值
                    Fi = []
                    for ic in _C:
                        s = Sch(self.J_num, self.Machine, self.State, self.PT)  # 创建作业调度对象
                        s.Decode(ic)  # 解码染色体得到作业调度方案
                        Fi.append(s.fitness)  # 计算子代的适应度值，并添加到Fi列表中

                    # 选择适应度最好的子代替换当前染色体
                    C[Ci] = _C[Fi.index(min(Fi))]  # 找到适应度最小的子代，替换当前染色体
                    Fit.append(min(Fi))  # 将最小的适应度值添加到Fit列表中（这里仍然存在问题，应该重新计算所有染色体的适应度）

                elif random.random() < self.Pm:  # 如果生成的随机数小于变异概率Pm
                    # 对当前染色体执行变异操作
                    CHS1 = self.Mutation(C[Ci])  # 调用Mutation方法，对染色体C[Ci]进行变异操作，返回变异后的染色体
                    C[Ci] = CHS1  # 将变异后的染色体替换原染色体
            # 在每一代迭代结束后，重新计算所有染色体的适应度值
            Fit = []  # 清空适应度值列表，准备重新计算
            Sc = []  # 初始化一个空列表，用于存放解码后的作业调度方案
            for C_i in C:
                s = Sch(self.J_num, self.Machine, self.State, self.PT)  # 创建作业调度对象
                s.Decode(C_i)  # 解码染色体得到作业调度方案
                Sc.append(s)  # 将解码后的作业调度方案添加到Sc列表中
                Fit.append(s.fitness)  # 计算染色体的适应度值，并添加到Fit列表中
            # 检查当前代的最佳适应度值是否优于之前的最佳值
            if min(Fit) < best_fit:
                best_fit = min(Fit)  # 更新最佳适应度值
                best_C = Sc[Fit.index(min(Fit))]  # 找到最佳适应度值对应的作业调度方案
            BF.append(best_fit)  # 将当前代的最佳适应度值添加到BF列表中
        # 绘制适应度值曲线
        plt.plot(x, BF)
        plt.show()
        best_C.Gantt()


if __name__ == "__main__":
    g = GA(Job, State, Machine, PT)
    g.main()
