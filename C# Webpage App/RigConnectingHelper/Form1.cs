using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace RigConnectingHelper
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
            rack1textBox.Text = Properties.Settings.Default.Rack1IP;
            rack2textBox.Text = Properties.Settings.Default.Rack2IP;
            rack3textBox.Text = Properties.Settings.Default.Rack3IP;
            rack4textBox.Text = Properties.Settings.Default.Rack4IP;
            rack5textBox.Text = Properties.Settings.Default.Rack5IP;
        }

        private void button1_Click(object sender, EventArgs e)
        {
            string target = "http://"+ rack1textBox.Text +":5000";
            System.Diagnostics.Process.Start(target);
            Properties.Settings.Default.Rack1IP = rack1textBox.Text;
            Properties.Settings.Default.Save();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            string target = "http://" + rack2textBox.Text + ":5000";
            System.Diagnostics.Process.Start(target);
            Properties.Settings.Default.Rack2IP = rack2textBox.Text;
            Properties.Settings.Default.Save();
        }

        private void button3_Click(object sender, EventArgs e)
        {
            string target = "http://" + rack3textBox.Text + ":5000";
            System.Diagnostics.Process.Start(target);
            Properties.Settings.Default.Rack3IP = rack3textBox.Text;
            Properties.Settings.Default.Save();
        }

        private void button4_Click(object sender, EventArgs e)
        {
            string target = "http://" + rack4textBox.Text + ":5000";
            System.Diagnostics.Process.Start(target);
            Properties.Settings.Default.Rack4IP = rack4textBox.Text;
            Properties.Settings.Default.Save();
        }

        private void button5_Click(object sender, EventArgs e)
        {
            string target = "http://" + rack5textBox.Text + ":5000";
            System.Diagnostics.Process.Start(target);
            Properties.Settings.Default.Rack5IP = rack5textBox.Text;
            Properties.Settings.Default.Save();
        }
    }
}
