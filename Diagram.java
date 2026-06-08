import java.awt.*;
import java.awt.geom.*;
import java.awt.image.*;
import javax.imageio.*;
import java.io.*;
import java.util.*;
import java.util.List;

public class Diagram {
    static final int SS = 2; // supersample factor for crisp output

    enum Shape { ROUNDED, DIAMOND, CYLINDER, STADIUM }

    static class Node {
        double cx, cy, w, h; Shape shape; Color fill, border; String[] lines;
        Node(double cx,double cy,double w,double h,Shape s,Color f,Color b,String... lines){
            this.cx=cx;this.cy=cy;this.w=w;this.h=h;this.shape=s;this.fill=f;this.border=b;this.lines=lines;
        }
        double left(){return cx-w/2;} double top(){return cy-h/2;}
    }

    static final Color PROC_F=new Color(220,230,247), PROC_B=new Color(48,84,150);
    static final Color DEC_F =new Color(252,228,182), DEC_B =new Color(191,143,0);
    static final Color DATA_F=new Color(214,233,206), DATA_B=new Color(84,130,53);
    static final Color START_F=new Color(226,226,226),START_B=new Color(90,90,90);
    static final Color OUT_F =new Color(228,223,241), OUT_B =new Color(112,48,160);
    static final Color CH_F  =new Color(208,236,238), CH_B  =new Color(33,115,120);
    static final Color STOP_F=new Color(245,221,221), STOP_B=new Color(192,80,77);

    static double[] edgePoint(Node n,double tx,double ty){
        double dx=tx-n.cx, dy=ty-n.cy;
        if(dx==0&&dy==0) return new double[]{n.cx,n.cy};
        double t;
        if(n.shape==Shape.DIAMOND){
            t=1.0/(Math.abs(dx)/(n.w/2)+Math.abs(dy)/(n.h/2));
        } else {
            double tx2=Math.abs(dx)<1e-9?1e9:(n.w/2)/Math.abs(dx);
            double ty2=Math.abs(dy)<1e-9?1e9:(n.h/2)/Math.abs(dy);
            t=Math.min(tx2,ty2);
        }
        return new double[]{n.cx+dx*t, n.cy+dy*t};
    }

    static void drawNode(Graphics2D g,Node n){
        double x=n.left(), y=n.top(), w=n.w, h=n.h;
        Shape2DResult shp;
        java.awt.Shape s;
        switch(n.shape){
            case STADIUM: s=new RoundRectangle2D.Double(x,y,w,h,h,h); break;
            case ROUNDED: s=new RoundRectangle2D.Double(x,y,w,h,16,16); break;
            case DIAMOND: {
                Path2D p=new Path2D.Double();
                p.moveTo(n.cx,y); p.lineTo(x+w,n.cy); p.lineTo(n.cx,y+h); p.lineTo(x,n.cy); p.closePath();
                s=p; break;
            }
            case CYLINDER: {
                double ry=9;
                Path2D p=new Path2D.Double();
                p.append(new Rectangle2D.Double(x,y+ry,w,h-2*ry),false);
                p.append(new Ellipse2D.Double(x,y,w,2*ry),false);
                p.append(new Ellipse2D.Double(x,y+h-2*ry,w,2*ry),false);
                g.setColor(n.fill); g.fill(p);
                g.setColor(n.border); g.setStroke(new BasicStroke(1.6f));
                g.draw(new Rectangle2D.Double(x,y+ry,0.01,h-2*ry)); // noop
                g.draw(new Line2D.Double(x,y+ry,x,y+h-ry));
                g.draw(new Line2D.Double(x+w,y+ry,x+w,y+h-ry));
                g.draw(new Ellipse2D.Double(x,y,w,2*ry));
                g.draw(new Arc2D.Double(x,y+h-2*ry,w,2*ry,180,180,Arc2D.OPEN));
                drawText(g,n); return;
            }
            default: s=new RoundRectangle2D.Double(x,y,w,h,16,16);
        }
        g.setColor(n.fill); g.fill(s);
        g.setColor(n.border); g.setStroke(new BasicStroke(1.6f)); g.draw(s);
        drawText(g,n);
    }
    static class Shape2DResult{}

    static void drawText(Graphics2D g,Node n){
        g.setColor(new Color(20,20,20));
        g.setFont(new Font("SansSerif",Font.PLAIN,13));
        FontMetrics fm=g.getFontMetrics();
        int lh=fm.getHeight()-3;
        int total=n.lines.length*lh;
        int sy=(int)Math.round(n.cy-total/2.0+fm.getAscent()-1);
        for(String ln:n.lines){
            int sw=fm.stringWidth(ln);
            g.drawString(ln,(int)Math.round(n.cx-sw/2.0),sy);
            sy+=lh;
        }
    }

    static void arrow(Graphics2D g,Node a,Node b,String label,boolean dashed,double... wp){
        double firstTx,firstTy,lastSx,lastSy;
        if(wp.length>=2){firstTx=wp[0];firstTy=wp[1];lastSx=wp[wp.length-2];lastSy=wp[wp.length-1];}
        else {firstTx=b.cx;firstTy=b.cy;lastSx=a.cx;lastSy=a.cy;}
        double[] start=edgePoint(a,firstTx,firstTy);
        double[] end=edgePoint(b,lastSx,lastSy);
        List<double[]> pts=new ArrayList<>();
        pts.add(start);
        for(int i=0;i+1<wp.length;i+=2) pts.add(new double[]{wp[i],wp[i+1]});
        pts.add(end);
        g.setColor(new Color(70,70,70));
        Stroke st = dashed? new BasicStroke(1.5f,BasicStroke.CAP_BUTT,BasicStroke.JOIN_ROUND,1f,new float[]{6f,5f},0f)
                          : new BasicStroke(1.6f);
        g.setStroke(st);
        Path2D path=new Path2D.Double();
        path.moveTo(pts.get(0)[0],pts.get(0)[1]);
        for(int i=1;i<pts.size();i++) path.lineTo(pts.get(i)[0],pts.get(i)[1]);
        g.draw(path);
        double[] p1=pts.get(pts.size()-2), p2=pts.get(pts.size()-1);
        arrowHead(g,p1[0],p1[1],p2[0],p2[1]);
        if(label!=null){
            double mx=(pts.get(0)[0]+pts.get(1)[0])/2, my=(pts.get(0)[1]+pts.get(1)[1])/2;
            g.setFont(new Font("SansSerif",Font.PLAIN,11));
            FontMetrics fm=g.getFontMetrics();
            int sw=fm.stringWidth(label);
            g.setColor(Color.WHITE);
            g.fill(new RoundRectangle2D.Double(mx-sw/2.0-3,my-fm.getAscent()/2.0-2,sw+6,fm.getAscent()+4,6,6));
            g.setColor(new Color(150,30,30));
            g.drawString(label,(int)Math.round(mx-sw/2.0),(int)Math.round(my+fm.getAscent()/2.0-1));
        }
    }

    static void arrowHead(Graphics2D g,double x1,double y1,double x2,double y2){
        double ang=Math.atan2(y2-y1,x2-x1), sz=10;
        double xa=x2-sz*Math.cos(ang-Math.PI/7), ya=y2-sz*Math.sin(ang-Math.PI/7);
        double xb=x2-sz*Math.cos(ang+Math.PI/7), yb=y2-sz*Math.sin(ang+Math.PI/7);
        Path2D p=new Path2D.Double(); p.moveTo(x2,y2); p.lineTo(xa,ya); p.lineTo(xb,yb); p.closePath();
        g.setColor(new Color(70,70,70)); g.fill(p);
    }

    interface DrawFn{ void draw(Graphics2D g); }

    static void render(String file,int W,int H,String title,DrawFn fn) throws IOException{
        BufferedImage img=new BufferedImage(W*SS,H*SS,BufferedImage.TYPE_INT_RGB);
        Graphics2D g=img.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
        g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING,RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
        g.setRenderingHint(RenderingHints.KEY_STROKE_CONTROL,RenderingHints.VALUE_STROKE_PURE);
        g.scale(SS,SS);
        g.setColor(Color.WHITE); g.fillRect(0,0,W,H);
        g.setColor(new Color(30,30,30));
        g.setFont(new Font("SansSerif",Font.BOLD,18));
        g.drawString(title,28,34);
        fn.draw(g);
        g.dispose();
        ImageIO.write(img,"png",new File(file));
        System.out.println("wrote "+file+" ("+(W*SS)+"x"+(H*SS)+")");
    }

    public static void main(String[] a) throws Exception {
        System.setProperty("java.awt.headless","true");

        // ---------- Diagram 1: CDP operating loop ----------
        render("cdp-operating-loop.png",1180,1180,"CDP operating loop (insurance)",g->{
            String[] srcLabels={"Policy admin / PAS","Claims","Billing / payments","Web + quote engine",
                "Mobile app","Call center / IVR","Agents / brokers","3rd-party / LexID"};
            Node[] src=new Node[8];
            for(int i=0;i<8;i++) src[i]=new Node(120,90+i*58,200,44,Shape.ROUNDED,PROC_F,PROC_B,srcLabels[i]);
            Node ingest=new Node(390,300,210,56,Shape.ROUNDED,PROC_F,PROC_B,"Ingest","real-time + batch");
            Node ident =new Node(390,398,310,64,Shape.ROUNDED,PROC_F,PROC_B,"Identity resolution","deterministic + probabilistic","household · agent-vs-direct");
            Node prof  =new Node(390,500,250,66,Shape.CYLINDER,DATA_F,DATA_B,"Unified customer","profile");
            Node intel =new Node(390,602,330,64,Shape.ROUNDED,PROC_F,PROC_B,"Intelligence","segments · propensity","churn · CLV · NBA");
            Node trig  =new Node(390,712,210,82,Shape.DIAMOND,DEC_F,DEC_B,"Trigger:","event / score");
            Node cons  =new Node(390,824,220,84,Shape.DIAMOND,DEC_F,DEC_B,"Consent +","governance gate");
            Node act   =new Node(390,928,240,54,Shape.ROUNDED,PROC_F,PROC_B,"Activation /","orchestration");
            Node supp  =new Node(720,824,170,50,Shape.ROUNDED,STOP_F,STOP_B,"Suppress");
            Node[] ch=new Node[5];
            String[][] chL={{"Email / SMS /","WhatsApp"},{"Web + app","personalization"},{"Push"},{"Call-center","screen pop"},{"Ad platforms","Customer Match / CAPI"}};
            for(int i=0;i<5;i++) ch[i]=new Node(130+i*215,1030,200,52,Shape.ROUNDED,CH_F,CH_B,chL[i]);
            Node out=new Node(560,1122,380,50,Shape.ROUNDED,OUT_F,OUT_B,"Outcomes + measurement","conversion · retention · ROAS · LTV");

            for(Node s:src) arrow(g,s,ingest,null,false);
            arrow(g,ingest,ident,null,false);
            arrow(g,ident,prof,null,false);
            arrow(g,prof,intel,null,false);
            arrow(g,intel,trig,null,false);
            arrow(g,trig,cons,null,false);
            arrow(g,cons,act,"allowed",false);
            arrow(g,cons,supp,"blocked",false);
            for(Node c:ch) arrow(g,act,c,null,false);
            for(Node c:ch) arrow(g,c,out,null,false);
            arrow(g,out,prof,"feedback + offline conversions",true,1130,1122,1130,500);

            for(Node s:src) drawNode(g,s);
            for(Node n:new Node[]{ingest,ident,prof,intel,trig,cons,act,supp,out}) drawNode(g,n);
            for(Node c:ch) drawNode(g,c);
        });

        // ---------- Diagram 2: quote-abandonment recovery + retargeting ----------
        render("cdp-abandonment-recovery.png",1180,1120,"Quote-abandonment recovery + retargeting flow",g->{
            Node V   =new Node(380,60,300,48,Shape.STADIUM,START_F,START_B,"Visitor starts online quote");
            Node Q   =new Node(380,142,300,48,Shape.ROUNDED,PROC_F,PROC_B,"Quote calculated / viewed");
            Node D   =new Node(380,242,210,86,Shape.DIAMOND,DEC_F,DEC_B,"Completed /","bound?");
            Node BIND=new Node(860,242,210,50,Shape.ROUNDED,DATA_F,DATA_B,"Policy bound");
            Node XS  =new Node(860,150,250,48,Shape.ROUNDED,PROC_F,PROC_B,"Onboarding + cross-sell");
            Node CAPI=new Node(860,344,270,56,Shape.ROUNDED,PROC_F,PROC_B,"Fire offline conversion (CAPI)","train value-based bidding");
            Node SUP =new Node(860,444,240,50,Shape.ROUNDED,STOP_F,STOP_B,"Suppress from acquisition ads");
            Node CAP =new Node(380,360,360,56,Shape.ROUNDED,PROC_F,PROC_B,"CDP captures abandon event","+ saves quote to profile");
            Node CONS=new Node(380,480,210,86,Shape.DIAMOND,DEC_F,DEC_B,"Consent to","contact?");
            Node AUD =new Node(770,576,300,56,Shape.ROUNDED,CH_F,CH_B,"Add to retargeting audience","Meta / Google Customer Match");
            Node SMS =new Node(330,600,320,50,Shape.ROUNDED,PROC_F,PROC_B,"SMS deep-link: resume");
            Node ESC =new Node(330,700,180,80,Shape.DIAMOND,DEC_F,DEC_B,"Engaged?");
            Node WA  =new Node(140,810,240,56,Shape.ROUNDED,PROC_F,PROC_B,"Escalate:","WhatsApp / email");
            Node CALL=new Node(140,910,240,56,Shape.ROUNDED,PROC_F,PROC_B,"Route to call-center","(agent briefed)");
            Node RET =new Node(380,828,220,48,Shape.ROUNDED,PROC_F,PROC_B,"Return to funnel");
            Node BAN =new Node(380,918,300,48,Shape.ROUNDED,PROC_F,PROC_B,"On-site resume banner");
            Node D2  =new Node(380,1018,190,82,Shape.DIAMOND,DEC_F,DEC_B,"Completes?");

            arrow(g,V,Q,null,false);
            arrow(g,Q,D,null,false);
            arrow(g,D,BIND,"Yes",false);
            arrow(g,D,CAP,"No / abandoned",false);
            arrow(g,BIND,XS,null,false);
            arrow(g,BIND,CAPI,null,false);
            arrow(g,CAPI,SUP,null,false);
            arrow(g,CAP,CONS,null,false);
            arrow(g,CAP,AUD,null,false);
            arrow(g,CONS,AUD,"No",false);
            arrow(g,CONS,SMS,"Yes",false);
            arrow(g,SMS,ESC,null,false);
            arrow(g,ESC,WA,"No",false);
            arrow(g,WA,CALL,null,false);
            arrow(g,ESC,RET,"Yes",false);
            arrow(g,CALL,RET,null,false);
            arrow(g,AUD,RET,null,false,760,828);
            arrow(g,RET,BAN,null,false);
            arrow(g,BAN,D2,null,false);
            arrow(g,D2,BIND,"Yes",false,1050,1018,1050,242);
            arrow(g,D2,BAN,"No",false,250,1018,250,918);

            for(Node n:new Node[]{V,Q,D,BIND,XS,CAPI,SUP,CAP,CONS,AUD,SMS,ESC,WA,CALL,RET,BAN,D2}) drawNode(g,n);
        });
    }
}
