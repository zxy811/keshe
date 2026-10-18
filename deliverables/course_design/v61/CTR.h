/*
液晶显示能力：128（列）x64（行）
屏幕坐标原点：左下角(0,0)
X轴坐标范围：0-127
Y轴坐标范围：0-63

编程说明：
0.程序中包含CTR.H头文件;cmd文件中加一行：-LCTR.lib
1.程序中开设屏幕缓冲区，类型为unsigned int，长度为1024
2.首先在程序中调用函数LCDSetScreenBuffer将屏幕缓冲区地址指针作为参数
3.调用LCDTurnOn打开显示
4.调用作图函数
5.调用LCDTurnOff关闭显示
*/

#define DATAINTMODE 0
#define DATAUINTMODE 1
#define LINEMODE 0
#define PIXELMODE 1
#define BARMODE 2

struct struLCDGraph	/* 图形显示参数 */
{
	void *pData;	/* 欲显示的数据起始地址指针 */
	unsigned int uDataMode;		/* 数据类型，可取DATAINTMODE：数据为int型；*/
								/*             取DATAUINTMODE：unsigned int型 */
	unsigned int uDataLength;	/* 数据个数 */
	unsigned int uMaxValue;		/* 最大值的绝对值 */
	unsigned int uWindowX0,uWindowY0,uWindowX1,uWindowY1;	/* 作图屏幕区域最大取值0,0,128,64 */
	int nOriginX,nOriginY;		/* 绘图坐标原点坐标 */
	unsigned int uLineMode;		/* 绘图线型：LINEMODE连线;PIXELMODE画点;BARMODE到横轴的垂直线 */
	unsigned int bShowXCcoordinate; /* 是否绘制x坐标轴 */
	unsigned int bShowYCcoordinate; /* 是否绘制y坐标轴 */
};

void LCDSetOrigin(int nX,int nY);	/* 重新设置原点位置，输入参数：新原点坐标 */
void LCDSetScreenBuffer(unsigned int *_pScreenBuffer);	/* 设置屏幕缓冲区指针，缓冲区为1024字（16bit/字） */
void LCDTurnOn();				/* 打开显示器 */
void LCDTurnOff();				/* 关闭显示器 */
void LCDCLS();					/* 清屏幕 */
void LCDSetDelay(unsigned int nDelay);	/* 设置液晶读写反应时间，参数:DSP主频8MHz时取0，160MHz时取1 */
void _Delay(unsigned int nTime);	/* 延时 */
void LCDRefreshScreen();	/* 用缓冲区中的数据刷新屏幕 */
void LCDPutPixel(int x,int y,unsigned int color);	/* 写点到屏幕，输入参数坐标值和颜色，颜色0消点,1画点,2异或画点 */
void LCDGraph(struct struLCDGraph *Gstru);	/* 按照定义的参数（在结构中）绘制图形 */
void LCDWriteBytes(unsigned int *pData,int x,int y,unsigned color);	/* 屏幕写字符8x8 */
void LCDPutCString(unsigned int *pData,int x,int y,unsigned int nCharNumber,unsigned color);	/* 屏幕写中文字符串，需要给出中文字数  */


